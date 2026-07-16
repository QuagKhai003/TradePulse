"""
dgcp.py — Dominican Republic DGCP (Compras Dominicana) procurement: market-specific buyers (DO market).
@context  Dominican OCDS API. Paged list of {ocid, url} + per-release detail (list-then-fetch, N+1). Items
          classified by UNSPSC -> approximate UNSPSC->HS crosswalk (sources/ocds._UNSPSC), like AusTender.
@golden   Buyer ORGANISATION + the official record link only — never a contact person.
@warn     N+1 + UNSPSC (best-effort product tags). `max_details` bounds the recent-window scan.
@limits   Network in _get only; mapping reuses ocds.parse_release.
@affects  Rows share TED's shape -> db.upsert_tenders / upsert_awards.
"""
from __future__ import annotations

import json
import time
import urllib.request

from .ocds import parse_release

LIST = ("https://datosabiertos.dgcp.gob.do/api-dgcp/v1/ocds/releases/all"
        "?limit=200&start_date={since}&end_date={until}&page={page}")


class DgcpSource:
    name = "do-dgcp"

    def __init__(self, timeout: int = 40, pause: float = 0.12, max_details: int = 400):
        self.timeout = timeout
        self.pause = pause
        self.max_details = max_details

    def pull(self, cpv_by_hs: dict[str, list[str]], since: str, until: str, scraped_at: str) -> tuple[list[dict], list[dict]]:
        """`since`/`until` = 'YYYY-MM-DD'. Page {ocid,url} refs, fetch each release, match its UNSPSC/CPV."""
        tenders: list[dict] = []
        awards: list[dict] = []
        fetched, page = 0, 1
        while fetched < self.max_details:
            lst = self._get(LIST.format(since=since, until=until, page=page))
            content = ((lst or {}).get("payload") or {}).get("content") or []
            if not content:
                break
            for row in content:
                if fetched >= self.max_details:
                    break
                url = row.get("url")
                if not url:
                    continue
                fetched += 1
                rels = (self._get(url) or {}).get("releases") or []
                if not rels:
                    continue
                r = rels[0]
                r.setdefault("tender", {}).setdefault("documents", []).append({"url": url})
                t, a = parse_release(r, "DOM", self.name, cpv_by_hs, scraped_at)
                tenders += t
                awards += a
                time.sleep(self.pause)
            if page >= int((lst or {}).get("pages") or 0):
                break
            page += 1
        print(f"[do-dgcp] scanned {fetched} tenders -> {len(tenders)} matched (DOM)")
        return tenders, awards

    def _get(self, url: str) -> dict | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 tradepulse/0.1",
                                                   "Accept": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — transient; retry
                if attempt < 2:
                    time.sleep(self.pause * 6)
                    continue
                print(f"[do-dgcp] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
