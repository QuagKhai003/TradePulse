"""
mtender.py — Moldova MTender public procurement: market-specific buyers (MD market).
@context  Moldova's open procurement (mtender.gov.md). Like Ukraine: no product filter, list-then-fetch.
          The list gives ocids + a date cursor; each detail is an OCDS record PACKAGE whose first
          `records[].compiledRelease` carries the buyer + a real CPV classification + title inline — so
          it reuses our CPV crosswalk (via ocds.parse_release). Keyless.
@warn     N+1. `max_details` bounds the recent window; coverage accretes over periodic batches. Paging is
          forward from `since` via the response's `offset` date cursor.
@golden   Buyer ORGANISATION + the official MTender link only — never a contact person.
@limits   Network in _get only; mapping reuses ocds.parse_release.
@affects  Rows share TED's shape -> db.upsert_tenders / upsert_awards.
"""
from __future__ import annotations

import json
import time
import urllib.request

from .ocds import parse_release

LIST = "https://public.mtender.gov.md/tenders/?offset={}"
DETAIL = "https://public.mtender.gov.md/tenders/{}"
PORTAL = "https://mtender.gov.md/tenders/{}"


class MtenderSource:
    name = "md-mtender"

    def __init__(self, timeout: int = 40, pause: float = 0.15, max_details: int = 400):
        self.timeout = timeout
        self.pause = pause
        self.max_details = max_details

    def pull(self, cpv_by_hs: dict[str, list[str]], since: str, scraped_at: str) -> tuple[list[dict], list[dict]]:
        """`since` = 'YYYY-MM-DD'. Page ocids forward from `since`, fetch each package, match its CPV."""
        tenders: list[dict] = []
        awards: list[dict] = []
        offset = f"{since}T00:00:00Z"
        fetched = 0
        while fetched < self.max_details:
            page = self._get(LIST.format(offset))
            data = (page or {}).get("data") or []
            if not data:
                break
            for row in data:
                if fetched >= self.max_details:
                    break
                ocid = row.get("ocid")
                if not ocid:
                    continue
                fetched += 1
                det = self._get(DETAIL.format(ocid))
                rel = self._compiled(det, ocid)
                if not rel:
                    continue
                t, a = parse_release(rel, "MDA", self.name, cpv_by_hs, scraped_at)
                tenders += t
                awards += a
                time.sleep(self.pause)
            nxt = (page or {}).get("offset")
            if not nxt or nxt == offset:
                break
            offset = nxt
        print(f"[md-mtender] scanned {fetched} tenders -> {len(tenders)} matched (MDA)")
        return tenders, awards

    @staticmethod
    def _compiled(det: dict | None, ocid: str) -> dict | None:
        """First record's compiledRelease (buyer + CPV + title), + a portal URL parse_release can pick up."""
        for r in (det or {}).get("records") or []:
            cr = r.get("compiledRelease")
            if cr and (cr.get("tender") or {}).get("title"):
                cr.setdefault("tender", {}).setdefault("documents", []).append({"url": PORTAL.format(ocid)})
                return cr
        return None

    def _get(self, url: str) -> dict | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 tradepulse/0.1",
                                                   "Accept": "application/json"})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — transient; back off once
                if attempt == 0:
                    time.sleep(self.pause * 6)
                    continue
                print(f"[md-mtender] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
