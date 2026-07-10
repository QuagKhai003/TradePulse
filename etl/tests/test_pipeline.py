"""
test_pipeline.py — deterministic, offline test for batch 1.1 (ETL -> trade_flows).
@context  Proves the fixture pipeline populates trade_flows correctly and is idempotent
          (re-run overwrites, never duplicates). No network, no clock.
@affects  Covers pipeline.run + db.upsert_trade_flows + transform.
"""
import tempfile
import unittest
from pathlib import Path

from tradepulse_etl import config
from tradepulse_etl.db import connect, count_trade_flows
from tradepulse_etl.pipeline import get_source, run


class PipelineTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)          # runs LAST (after conn.close below)
        self.db = Path(tmp.name) / "t.sqlite"
        self.raw = Path(tmp.name) / "raw"

    def _connect(self):
        conn = connect(self.db)
        self.addCleanup(conn.close)           # runs FIRST (LIFO) so Windows can unlink the file
        return conn

    def test_populate_and_idempotent(self):
        conn = self._connect()
        src = get_source("fixture")

        n1 = run(src, conn, raw_dir=self.raw)
        self.assertEqual(n1, 84)                      # 5 world + JP(5)+KR(4) partner series x 6 quarters
        self.assertEqual(count_trade_flows(conn), 84)

        # Known cell: Japan (392) x World (0) x 2026-Q1 import = $700M.
        row = conn.execute(
            "SELECT value_usd, source, published_date FROM trade_flows "
            "WHERE reporter=? AND partner=? AND period=? AND flow=?",
            (392, config.PARTNER_WORLD, "2026-Q1", config.FLOW_IMPORT),
        ).fetchone()
        self.assertEqual(row["value_usd"], 700_000_000)
        self.assertEqual(row["source"], "fixture")
        self.assertEqual(row["published_date"], "2026-05-15")

        # Idempotent: a second run keeps the row count identical (upsert, not insert).
        run(src, conn, raw_dir=self.raw)
        self.assertEqual(count_trade_flows(conn), 84)

    def test_raw_persisted_before_transform(self):
        conn = self._connect()
        run(get_source("fixture"), conn, raw_dir=self.raw)
        self.assertTrue((self.raw / "fixture.json").exists())


if __name__ == "__main__":
    unittest.main()
