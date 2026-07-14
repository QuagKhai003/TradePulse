"""
eurostat.py — EU source via Eurostat Comext dataset DS-059341 (the live successor to the retired
DS-045409). API only, NO bulk download.
@context  Fresher + authoritative for the EU (reporter 97) than the Comtrade API. Comext reports the
          EU27 as one bloc (`EU27_2020`) trading with the rest of the world (`EXT_EU27_2020` = extra-EU)
          — exactly our World-partner demand measure. Monthly, fresh to ~last month (Apr 2026 when
          wired). Values are EUR -> USD via fx.to_usd so they merge with Comtrade/Census/KCS.
@warn     Partner MUST be EXT_EU27_2020 (extra-EU), NOT the all-partner total (includes intra-EU).
          The OLD dataset DS-045409 now faults (140); DS-059341 is the current one (dims:
          freq.reporter.partner.product.flow.indicators; indicator VALUE_EUR). Product accepts HS4 or HS6.
@done     pull() -> Comtrade-shaped raw rows (reporter=97, partner=World); _parse() pure + tested.
@limits   Network in _get + ECBFx. Skips TOTAL (Comtrade covers it). SDMX-CSV (stdlib csv). Keyless.
@affects  Implements the source protocol; merged in the pipeline. Tested by tests/test_eurostat.py.
"""
from __future__ import annotations

import csv
import io
import time
import urllib.parse
import urllib.request
from datetime import date

from ..fx import ECBFx, to_usd

EU_REPORTER = 97
WORLD = 0
BASE = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/2.1/data/DS-059341"
_FLOW = {"1": "M", "2": "X"}      # Comext flow code -> our flow


class EurostatSource:
    name = "eurostat"

    def __init__(self, years: int = 3, timeout: int = 60, pause: float = 0.4,
                 freqs: tuple[str, ...] = ("A",), fx: dict | None = None):
        self.years = years
        self.timeout = timeout
        self.pause = pause
        self.freqs = freqs
        self._fx = fx

    def _usd_per_eur(self) -> dict:
        if self._fx is None:
            self._fx = ECBFx().rates(freqs=("A",), currencies=("USD",))
        return self._fx.get("USD", {})

    def pull(self, hs_codes: list[str], reporters: list[int], partners: list[int] | None,
             skip: frozenset = frozenset()) -> list[dict]:
        usd = self._usd_per_eur()
        start = f"{date.today().year - self.years}-01"
        rows: list[dict] = []
        for hs in hs_codes:
            if hs == "TOTAL":
                continue
            # one call per product: flow blank -> both flows, monthly, value only.
            key = f"M.EU27_2020.EXT_EU27_2020.{hs}..VALUE_EUR"
            url = f"{BASE}/{key}?" + urllib.parse.urlencode({"format": "SDMX-CSV", "startPeriod": start})
            text = self._get(url)
            if text:
                rows += self._parse(text, hs, usd, self.freqs)
            time.sleep(self.pause)
        return rows

    # --- pure: SDMX-CSV -> USD rows, monthly EUR aggregated to complete quarters + years ---
    @staticmethod
    def _parse(text: str, hs: str, usd_per_eur: dict, freqs: tuple) -> list[dict]:
        month_eur: dict[tuple, float] = {}     # (flow, 'YYYY-MM') -> EUR
        for r in csv.DictReader(io.StringIO(text)):
            flow = _FLOW.get((r.get("flow") or "").strip())
            period = (r.get("TIME_PERIOD") or "").strip()      # 'YYYY-MM'
            if not flow or len(period) != 7:
                continue
            try:
                eur = float(r.get("OBS_VALUE") or 0)
            except ValueError:
                continue
            if eur > 0:
                month_eur[(flow, period)] = month_eur.get((flow, period), 0.0) + eur

        out: list[dict] = []

        def emit(flow: str, period: str, eur: float) -> None:
            # FX table is annual (keyed by year); convert with the period's YEAR (period may be a
            # quarter like '2026-Q1' or a year '2026').
            usd = to_usd(eur, "EUR", period[:4], usd_per_eur, {})
            if usd and usd > 0:
                out.append({"reporterCode": EU_REPORTER, "partnerCode": WORLD, "cmdCode": hs,
                            "period": period, "flowCode": flow, "primaryValue": round(usd, 2),
                            "netWgt": None, "qtyUnitAbbr": None, "publishedDate": None})

        if "Q" in freqs:
            q: dict[tuple, list] = {}
            for (flow, ym), v in month_eur.items():
                y, m = ym.split("-")
                q.setdefault((flow, f"{y}-Q{(int(m) - 1) // 3 + 1}"), []).append(v)
            for (flow, period), vals in q.items():
                if len(vals) >= 3:                              # complete quarter only
                    emit(flow, period, sum(vals))
        if "A" in freqs:
            yr: dict[tuple, list] = {}
            for (flow, ym), v in month_eur.items():
                yr.setdefault((flow, ym[:4]), []).append(v)
            for (flow, period), vals in yr.items():
                if len(vals) >= 12:                             # complete year only
                    emit(flow, period, sum(vals))
        return out

    def _get(self, url: str) -> str | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return r.read().decode("utf-8")
            except Exception as e:  # noqa: BLE001 — no-data products 404; skip
                if attempt == 0:
                    time.sleep(self.pause * 3)
                    continue
                print(f"[eurostat] warn: {type(e).__name__}:{getattr(e, 'code', '')} for {url[:70]}")
                return None
