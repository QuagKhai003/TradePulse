"""
test_eurostat.py — EU Comext (DS-059341) SDMX-CSV parse + EUR->USD (sources/eurostat.py). Pure, offline.
@context  Proves _parse turns the SDMX-CSV response into Comtrade-shaped USD rows for the EU (reporter
          97, World partner = extra-EU), converting EUR->USD by the period's YEAR, aggregating the
          monthly values to complete quarters + years.
"""
import unittest

from tradepulse_etl.sources.eurostat import EurostatSource

# SDMX-CSV as DS-059341 returns it: header + monthly rows. flow 1=import, product 090111, VALUE_EUR.
# Six months of import data -> two complete quarter rows; not a full year -> no annual row.
CSV = "DATAFLOW,LAST UPDATE,freq,reporter,partner,product,flow,indicators,TIME_PERIOD,OBS_VALUE\n" + "\n".join(
    f"ESTAT:DS-059341(1.0),15/06/26,M,DE,WORLD,090111,1,VALUE_EUR,2026-{m:02d},1000000000"
    for m in range(1, 7)
)
USD_PER_EUR = {"2026": 1.10}


class EurostatParseTest(unittest.TestCase):
    def test_quarters_aggregated_and_converted(self):
        out = EurostatSource._parse(CSV, "090111", USD_PER_EUR, ("A", "Q"))
        by = {r["period"]: r for r in out}
        self.assertIn("2026-Q1", by)
        self.assertIn("2026-Q2", by)
        self.assertNotIn("2026", by)                       # only 6 months -> no complete year
        q1 = by["2026-Q1"]
        self.assertEqual(q1["reporterCode"], 276)          # Germany (DE -> M49)
        self.assertEqual(q1["partnerCode"], 0)             # World (extra-EU)
        self.assertEqual(q1["flowCode"], "M")
        self.assertAlmostEqual(q1["primaryValue"], round(3_000_000_000 * 1.10, 2))  # 3 months x EUR->USD

    def test_complete_year_emitted(self):
        csv12 = "DATAFLOW,LAST UPDATE,freq,reporter,partner,product,flow,indicators,TIME_PERIOD,OBS_VALUE\n" + "\n".join(
            f"x,x,M,DE,WORLD,090111,1,VALUE_EUR,2025-{m:02d},1000000000" for m in range(1, 13))
        out = EurostatSource._parse(csv12, "090111", {"2025": 1.0}, ("A",))
        yr = next(r for r in out if r["period"] == "2025")
        self.assertEqual(yr["primaryValue"], 12_000_000_000)

    def test_missing_rate_drops(self):
        out = EurostatSource._parse(CSV, "090111", {}, ("Q",))   # no FX rate -> nothing convertible
        self.assertEqual(out, [])

    def test_empty(self):
        self.assertEqual(EurostatSource._parse("", "090111", USD_PER_EUR, ("Q",)), [])


if __name__ == "__main__":
    unittest.main()
