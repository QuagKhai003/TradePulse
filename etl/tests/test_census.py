"""
test_census.py — US Census aggregation (sources/census.py). Pure, offline (no network).
@context  Proves the Census array-of-arrays parses into ONE World-total raw row per (hs, year, flow):
          sums every partner country, skips the header + Census 'total' sentinel (no double-count),
          and yields a Comtrade-shaped record the transform/merge steps understand.
"""
import unittest

from tradepulse_etl.sources.census import USCensusSource

# Census-shaped response: header row, then [CTY_CODE, value] per country. '-' = total sentinel.
TABLE = [
    ["CTY_CODE", "ALL_VAL_YR"],
    ["5700", "1000"],     # a country
    ["5880", "2500"],     # another country
    ["-", "3500"],        # 'TOTAL FOR ALL COUNTRIES' sentinel — must be skipped, not summed
]


class CensusTest(unittest.TestCase):
    def test_world_total_sums_countries_only(self):
        out = USCensusSource._aggregate(TABLE, "090111", 2025, "X", "ALL_VAL_YR")
        self.assertEqual(len(out), 1)
        row = out[0]
        self.assertEqual(row["reporterCode"], 842)
        self.assertEqual(row["partnerCode"], 0)               # World
        self.assertEqual(row["cmdCode"], "090111")
        self.assertEqual(row["period"], "2025")
        self.assertEqual(row["flowCode"], "X")
        self.assertEqual(row["primaryValue"], 3500.0)         # 1000 + 2500, NOT 7000 (sentinel skipped)
        self.assertEqual(row["publishedDate"], "2025-12")

    def test_empty_or_headeronly_yields_nothing(self):
        self.assertEqual(USCensusSource._aggregate([], "090111", 2025, "X", "ALL_VAL_YR"), [])
        self.assertEqual(USCensusSource._aggregate([["CTY_CODE", "ALL_VAL_YR"]], "090111", 2025, "X", "ALL_VAL_YR"), [])

    def test_zero_total_dropped(self):
        table = [["CTY_CODE", "GEN_VAL_YR"], ["5700", "0"]]
        self.assertEqual(USCensusSource._aggregate(table, "440131", 2024, "M", "GEN_VAL_YR"), [])


if __name__ == "__main__":
    unittest.main()
