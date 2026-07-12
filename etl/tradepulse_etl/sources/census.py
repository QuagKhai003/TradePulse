"""
census.py — US Census International Trade source (first fresh NATIONAL primary; docs/DATA_SOURCES §1b).
@context  The US is the authority on its own trade, monthly + fresher than Comtrade annual, and the
          data is US public domain (cleanest licence we have). This adapter pulls annual US totals per
          covered HS (both flows) so the merge step lets it OVERRIDE Comtrade for reporter=842. Grain
          here is annual (value-to-date at MONTH=12); quarterly/monthly + per-partner breakdown are the
          next increment (kept out now to avoid shipping a guessed country-code crosswalk = wrong data).
@done     pull() -> Comtrade-shaped raw rows (reporter=842, partner=World); _aggregate() pure + tested.
@limits   Network I/O in _get only. US-only (ignores other reporters). Needs CENSUS_API_KEY (free).
@affects  Implements base.TradeSource; merged with Comtrade in pipeline. Tested by tests/test_census.py.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date

US_REPORTER = 842
WORLD = 0
EXPORTS = "https://api.census.gov/data/timeseries/intltrade/exports/hs"
IMPORTS = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
# flow -> (endpoint, commodity var, annual value var)
_FLOW = {
    "X": (EXPORTS, "E_COMMODITY", "ALL_VAL_YR"),
    "M": (IMPORTS, "I_COMMODITY", "GEN_VAL_YR"),
}


class USCensusSource:
    name = "census"

    def __init__(self, key: str | None = None, years: int = 6, timeout: int = 60, pause: float = 0.6):
        self.key = key
        self.years = years
        self.timeout = timeout
        self.pause = pause

    def pull(self, hs_codes: list[str], reporters: list[int], partners: list[int] | None) -> list[dict]:
        if not self.key:
            print("[census] no CENSUS_API_KEY — skipping (keyless is rejected by the API)")
            return []
        rows: list[dict] = []
        for hs in hs_codes:
            if hs == "TOTAL":            # Census HS endpoint has no all-commodities total — leave to Comtrade
                continue
            comm_lvl = f"HS{len(hs)}"    # HS4 category vs HS6 product
            for year in self._recent_years(self.years):
                for flow, (url, comm_var, val_var) in _FLOW.items():
                    params = {"get": f"CTY_CODE,{val_var}", comm_var: hs, "YEAR": str(year),
                              "MONTH": "12", "COMM_LVL": comm_lvl, "key": self.key}
                    table = self._get(f"{url}?{urllib.parse.urlencode(params)}")
                    rows += self._aggregate(table, hs, year, flow, val_var)
                    time.sleep(self.pause)
        return rows

    # --- pure: Census array-of-arrays -> one World-total raw row per (hs, year, flow) ---
    @staticmethod
    def _aggregate(table: list[list], hs: str, year: int, flow: str, val_var: str) -> list[dict]:
        """Sum the annual value over every partner country -> the US World total. Order-independent;
        skips the header row and any Census 'total-for-all-countries' sentinel to avoid double-count."""
        if not table or len(table) < 2:
            return []
        header = table[0]
        try:
            vi = header.index(val_var)
            ci = header.index("CTY_CODE")
        except ValueError:
            return []
        total = 0.0
        for r in table[1:]:
            code = str(r[ci]).strip()
            if not code.isdigit():       # '-' / 'X' = Census total sentinel — skip (we sum ourselves)
                continue
            try:
                total += float(r[vi])
            except (TypeError, ValueError):
                continue
        if total <= 0:
            return []
        return [{
            "reporterCode": US_REPORTER, "partnerCode": WORLD, "cmdCode": hs, "period": str(year),
            "flowCode": flow, "primaryValue": round(total, 2), "netWgt": None,
            "qtyUnitAbbr": None, "publishedDate": f"{year}-12",
        }]

    def _get(self, url: str) -> list[list]:
        headers = {"User-Agent": "tradepulse/0.1"}
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode("utf-8")) or []
            except Exception as e:  # noqa: BLE001 — transient/no-data (Census 204s an empty HS+year)
                if attempt == 0:
                    time.sleep(self.pause * 3)
                    continue
                print(f"[census] warn: {type(e).__name__}:{getattr(e, 'code', '')} for {url[:90]}")
                return []

    @staticmethod
    def _recent_years(n: int) -> list[int]:
        y = date.today().year
        return list(range(y - n, y))
