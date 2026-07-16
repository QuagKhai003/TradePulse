"""
chilecompra.py — Chile ChileCompra/Mercado Público procurement: market-specific buyers (CL market).
@context  Chile's OCDS API. Month-paged list of ocids + per-tender detail (list-then-fetch, N+1). Items
          classified by UNSPSC -> approximate UNSPSC->HS crosswalk (sources/ocds._UNSPSC), like AusTender.
          The list gives an official tender URL (forced to https; the http host resets connections).
@golden   Buyer ORGANISATION + the official record link only — never a contact person.
@warn     N+1 + UNSPSC (best-effort product tags). `max_details` bounds the recent-months scan.
@limits   Network in _get only; mapping reuses ocds.parse_release.
@affects  Rows share TED's shape -> db.upsert_tenders / upsert_awards.
"""
from __future__ import annotations

import json
import time
import urllib.request

from .ocds import parse_release

LIST = "https://api.mercadopublico.cl/APISOCDS/OCDS/listaOCDSAgnoMes/{year}/{month}/{offset}/{limit}"


class ChileCompraSource:
    name = "cl-chilecompra"

    def __init__(self, timeout: int = 40, pause: float = 0.12, max_details: int = 400):
        self.timeout = timeout
        self.pause = pause
        self.max_details = max_details

    def pull(self, cpv_by_hs: dict[str, list[str]], since: str, scraped_at: str) -> tuple[list[dict], list[dict]]:
        """`since` = 'YYYY-MM-DD'. Scan recent months, list ocids, fetch each detail, match its UNSPSC/CPV."""
        tenders: list[dict] = []
        awards: list[dict] = []
        fetched = 0
        y0, m0 = int(since[:4]), int(since[5:7])
        # months from `since` up to the window end, newest first-ish
        months = [(2026, m) for m in range(m0, 13)] if y0 == 2026 else [(y0, m0)]
        for year, month in reversed(months):
            offset = 0
            while fetched < self.max_details:
                page = self._get(LIST.format(year=year, month=month, offset=offset, limit=100))
                data = (page or {}).get("data") or []
                if not data:
                    break
                for row in data:
                    if fetched >= self.max_details:
                        break
                    ref = (row.get("urlTender") or "").replace("http://", "https://")
                    if not ref:
                        continue
                    fetched += 1
                    det = self._get(ref)
                    rel = (det or {}).get("releases") or []
                    if not rel:
                        continue
                    r = rel[0]
                    r.setdefault("tender", {}).setdefault("documents", []).append({"url": ref})
                    t, a = parse_release(r, "CHL", self.name, cpv_by_hs, scraped_at)
                    tenders += t
                    awards += a
                    time.sleep(self.pause)
                total = ((page or {}).get("pagination") or {}).get("total", 0)
                offset += 100
                if offset >= int(total or 0):
                    break
            if fetched >= self.max_details:
                break
        print(f"[cl-chilecompra] scanned {fetched} tenders -> {len(tenders)} matched (CHL)")
        return tenders, awards

    def _get(self, url: str) -> dict | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 tradepulse/0.1",
                                                   "Accept": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — http host resets; retry a couple times
                if attempt < 2:
                    time.sleep(self.pause * 8)
                    continue
                print(f"[cl-chilecompra] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
