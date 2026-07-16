"""
test_sourcing.py — the quarterly partner-sourcing aggregation + the TOTAL-quarterly promotion. Pure.
@context  build_sourcing turns quarterly bilateral flows into top-partner tables + a stacked series.
          total_quarterly_flows then reconstructs each focus reporter's World total per quarter from
          that series (sum of top partners + 'Other'), as trade_flow rows — the ONLY way the 'all
          products' (TOTAL) view gets a Year/Quarter toggle without a second heavy Comtrade pull.
@limits   Offline; pure functions. No I/O.
@affects  tradepulse_etl/sources...pull_sourcing -> build_sourcing -> total_quarterly_flows -> snapshot.
"""
import unittest

from tradepulse_etl import config
from tradepulse_etl.sourcing import total_quarterly_flows

# A built sourcing map for one focus reporter (USA), export side only. World total per period is the
# sum of the stacked series (two named partners + 'Other'): Q1 = 10+5+3 = 18, Q2 = 12+6+4 = 22.
SM = {
    "842": {
        "export": {
            "periods": ["2024", "2025-Q1", "2025-Q2"],   # a stray annual period must be ignored
            "partners": [],
            "series": [
                {"code": 484, "values": [99.0, 10.0, 12.0]},
                {"code": 124, "values": [99.0, 5.0, 6.0]},
                {"code": -1, "name_en": "Other", "values": [99.0, 3.0, 4.0]},
            ],
        },
        "import": None,
    },
}


class TotalQuarterlyFlowsTest(unittest.TestCase):
    def setUp(self):
        self.rows = total_quarterly_flows(SM, "TOTAL", "2026-07-16T00:00:00+00:00")

    def test_one_row_per_quarter_annual_skipped(self):
        self.assertEqual([r["period"] for r in self.rows], ["2025-Q1", "2025-Q2"])   # no "2024"

    def test_world_total_is_sum_of_series(self):
        self.assertEqual([r["value_usd"] for r in self.rows], [18.0, 22.0])

    def test_row_shape_matches_trade_flow_world_partner(self):
        r = self.rows[0]
        self.assertEqual(r["reporter"], 842)
        self.assertEqual(r["partner"], config.PARTNER_WORLD)     # _flows reads World-partner rows only
        self.assertEqual(r["hs6"], "TOTAL")
        self.assertEqual(r["freq"], "Q")
        self.assertEqual(r["flow"], config.FLOW_EXPORT)
        self.assertEqual(r["published_date"], "2026-07-16")

    def test_empty_or_missing_block_yields_nothing(self):
        self.assertEqual(total_quarterly_flows({"704": {"export": None, "import": None}}, "TOTAL", "d"), [])

    def test_zero_world_period_dropped(self):
        sm = {"392": {"export": {"periods": ["2025-Q1"], "series": [{"code": 1, "values": [0.0]}]}}}
        self.assertEqual(total_quarterly_flows(sm, "TOTAL", "d"), [])


if __name__ == "__main__":
    unittest.main()
