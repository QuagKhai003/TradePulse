"""
psd.py — FORWARD lane: USDA FAS PSD global supply/demand OUTLOOK (production/imports/exports/consumption/
         stocks by market year, INCLUDING the forecast year).
@context  Customs stats are backward-looking; PSD publishes a FORWARD balance — who is forecast to
          produce, import, consume, and hold stocks next market year. A SEPARATE lane (ADR-0007): a
          quantity outlook, never merged into the customs $ signal, shown beside the flow figures as a
          demand cue. AG commodities only (coffee, rice, grains, oilseeds, cotton, sugar, poultry); the
          rest of the catalog honestly shows none — same as the IMF price lane.
@source   api.fas.usda.gov PSD API, key in the X-Api-Key HEADER (USDA_API_KEY — any api.data.gov key
          works; NOT a query param, NOT api.data.gov's host). One call per (commodity, country, market
          year): /api/psd/commodity/{code}/country/{cc}/year/{y}; World uses /world/year/{y}. Public
          USDA data + official source link (Golden Rule). Deterministic given a response.
@limits   Network in _get only; pure otherwise. A missing (commodity, country, year) 404s -> skipped.
@affects  Stored via db.upsert_psd_outlook; exported to psd-<hs>.json by export.build_psd.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import date

from .. import config

BASE = "https://api.fas.usda.gov/api/psd"
CITE = "https://apps.fas.usda.gov/psdonline/app/index.html"


class PsdSource:
    name = "usda-psd"

    def __init__(self, key: str, timeout: int = 40, pause: float = 0.12):
        self.key = key
        self.timeout = timeout
        self.pause = pause

    def pull(self, psd_hs: dict[str, str], markets: dict[int, str], attrs: dict,
             years: int = config.PSD_YEARS, verified_date: str | None = None,
             today: date | None = None) -> list[dict]:
        """For each mapped commodity × market × recent market year, keep the headline attributes."""
        today = today or date.today()
        verified_date = verified_date or today.isoformat()
        units = self._units()
        wanted = set(attrs)
        yrs = list(range(today.year - years + 2, today.year + 2))   # short history + the forecast year
        rows: list[dict] = []
        for hs, com in psd_hs.items():
            kept = 0
            for m49, cc in markets.items():
                for y in yrs:
                    for r in self._data(com, cc, y) or []:
                        aid = r.get("attributeId")
                        if aid not in wanted or r.get("value") is None:
                            continue
                        rows.append({
                            "hs4": hs, "commodity": com, "market": m49,
                            "market_year": str(r.get("marketYear") or y),
                            "attribute_id": aid, "value": float(r["value"]),
                            "unit": (units.get(r.get("unitId")) or "").strip(),
                            "source": self.name, "verified_date": verified_date,
                        })
                        kept += 1
            print(f"[psd] {hs} ({com}): {kept} outlook points")
        return rows

    def _data(self, com: str, cc: str, year: int) -> list | None:
        path = (f"{BASE}/commodity/{com}/world/year/{year}" if cc == "00"
                else f"{BASE}/commodity/{com}/country/{cc}/year/{year}")
        return self._get(path)

    def _units(self) -> dict[int, str]:
        u = self._get(f"{BASE}/unitsOfMeasure") or []
        return {x["unitId"]: x.get("unitDescription", "") for x in u}

    def _get(self, url: str):
        req = urllib.request.Request(url, headers={
            "X-Api-Key": self.key, "Accept": "application/json", "User-Agent": "tradepulse/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 404:                       # 404 = no data for this commodity/country/year (normal)
                print(f"[psd] warn HTTP {e.code} on …{url[-52:]}")
            return None
        except Exception as e:  # noqa: BLE001 — one shot; a missing outlook line is never fatal
            print(f"[psd] warn {type(e).__name__} on …{url[-52:]}")
            return None
        finally:
            time.sleep(self.pause)
