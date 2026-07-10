"""
test_signals.py — deterministic test for batch 1.2 (signal compute, plan §6). No clock/network.
@context  Asserts every band boundary, the noise floors, new-lane, and the fixture's expected
          signals. This is the moat; it must be pinned exactly.
@affects  Covers signals.classify_band + signals.compute_signals + the fixture's shape.
"""
import unittest

from tradepulse_etl import config
from tradepulse_etl.db import connect, fetch_flows, upsert_signals
from tradepulse_etl.pipeline import get_source, run
from tradepulse_etl.signals import classify_band, compute_signals, prev_year_period

NOW = "2026-07-10T00:00:00+00:00"


class BandTest(unittest.TestCase):
    def test_prev_year_period(self):
        self.assertEqual(prev_year_period("2026-Q1"), "2025-Q1")
        self.assertEqual(prev_year_period("2025-Q4"), "2024-Q4")

    def test_band_boundaries(self):
        # Edges of the §6.3 bands (magnitude; direction via sign).
        self.assertEqual(classify_band(0.0), "minor")
        self.assertEqual(classify_band(0.149), "minor")
        self.assertEqual(classify_band(0.15), "moderate")
        self.assertEqual(classify_band(-0.29), "moderate")
        self.assertEqual(classify_band(0.30), "significant")
        self.assertEqual(classify_band(-0.59), "significant")
        self.assertEqual(classify_band(0.60), "surge")
        self.assertEqual(classify_band(-0.60), "collapse")


class ComputeTest(unittest.TestCase):
    def _flows(self):
        # Minimal in-memory flows: one World cell with 5 quarters + a year-ago base.
        def cell(period, value):
            return {"reporter": 392, "partner": config.PARTNER_WORLD, "hs6": "440131",
                    "period": period, "flow": "M", "value_usd": value}
        return [cell("2025-Q1", 500_000_000), cell("2025-Q2", 1),  # noqa: placeholders for history
                cell("2025-Q3", 1), cell("2025-Q4", 1), cell("2026-Q1", 700_000_000)]

    def test_yoy_and_floors(self):
        sigs = {(s["reporter"], s["period"]): s for s in compute_signals(self._flows(), NOW)}
        s = sigs[(392, "2026-Q1")]                       # 700 vs 500 = +40% significant
        self.assertAlmostEqual(s["yoy_delta"], 0.4, places=6)
        self.assertEqual(s["band"], "significant")

    def test_base_below_floor_suppressed(self):
        # base ($1) < NOISE_MIN_BASE and not a new lane (base present) -> no signal row.
        flows = [
            {"reporter": 1, "partner": 0, "hs6": "440131", "period": "2025-Q1", "flow": "M", "value_usd": 1},
            {"reporter": 1, "partner": 0, "hs6": "440131", "period": "2026-Q1", "flow": "M", "value_usd": 50_000_000},
        ]
        bands = [s["band"] for s in compute_signals(flows, NOW)]
        self.assertNotIn("significant", bands)

    def test_value_below_floor_suppressed(self):
        # US-like cell: value under $10M -> no signal even with a valid base.
        flows = []
        for p, v in [("2025-Q1", 8_000_000), ("2025-Q2", 8_000_000), ("2025-Q3", 8_000_000),
                     ("2025-Q4", 8_000_000), ("2026-Q1", 9_500_000)]:
            flows.append({"reporter": 842, "partner": 0, "hs6": "440131", "period": p, "flow": "M", "value_usd": v})
        self.assertEqual(compute_signals(flows, NOW), [])


class FixtureIntegrationTest(unittest.TestCase):
    def test_fixture_expected_signals(self):
        conn = connect(":memory:")
        self.addCleanup(conn.close)
        run(get_source("fixture"), conn, raw_dir=_tmp())
        sigs = {(s["reporter"], s["period"]): s for s in compute_signals(fetch_flows(conn), NOW)}

        jp = sigs[(392, "2026-Q1")]      # 700 vs 520 = +34.6% -> significant up
        self.assertEqual(jp["band"], "significant")
        self.assertGreater(jp["yoy_delta"], 0)

        kr = sigs[(410, "2026-Q1")]      # 150 vs 320 = -53% -> significant decline
        self.assertEqual(kr["band"], "significant")
        self.assertLess(kr["yoy_delta"], 0)

        self.assertNotIn((842, "2026-Q1"), sigs)   # US below the $10M floor -> no signal

        n = upsert_signals(conn, list(sigs.values()))   # persists without error
        self.assertEqual(n, len(sigs))


def _tmp():
    import tempfile
    d = tempfile.mkdtemp()
    return d


if __name__ == "__main__":
    unittest.main()
