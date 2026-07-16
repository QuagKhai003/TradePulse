"""
austender.py — Australia AusTender public procurement: market-specific buyers/awards (AU market).
@context  AusTender publishes OCDS contract releases (the awarding agency = buyer, the supplier = seller),
          paged by date + cursor — INLINE (no per-tender fetch, unlike UA/MD). Classifies items by
          UNSPSC, so it matches via the approximate UNSPSC->HS crosswalk (sources/ocds._UNSPSC), NOT the
          CPV crosswalk — product tags are best-effort for this market. Releases carry no link, so we
          construct the AusTender CN URL from the ocid. Keyless (needs the /contractPublished/ path).
@warn     AU procurement is service-heavy; only ~18% of items are HS goods, so yield is goods-only. The
          CN portal is WAF-protected (403 to bots) but opens in a browser — same accepted trade-off as TED.
@golden   Buyer + supplier ORGANISATION + the official notice link only — never a contact person.
@limits   Network in _get only; mapping reuses ocds.parse_release.
@affects  Rows share TED's shape -> db.upsert_tenders / upsert_awards.
"""
from __future__ import annotations

import json
import time
import urllib.request

from .ocds import parse_release

BASE = "https://api.tenders.gov.au/ocds/findByDates/contractPublished/{}T00:00:00Z/2027-01-01T00:00:00Z"
PORTAL = "https://www.tenders.gov.au/Cn/Show/{}"


class AusTenderSource:
    name = "au-tenders"

    def __init__(self, timeout: int = 40, pause: float = 0.3, max_pages: int = 30):
        self.timeout = timeout
        self.pause = pause
        self.max_pages = max_pages

    def pull(self, cpv_by_hs: dict[str, list[str]], since: str, scraped_at: str) -> tuple[list[dict], list[dict]]:
        """`since` = 'YYYY-MM-DD'. Page contract releases (inline), match items' UNSPSC -> HS, tag AUS."""
        tenders: list[dict] = []
        awards: list[dict] = []
        url = BASE.format(since)
        for _ in range(self.max_pages):
            d = self._get(url)
            if not d:
                break
            for rel in d.get("releases") or []:
                oc = (rel.get("ocid") or "").split("prod-")[-1]
                if oc:                                       # AusTender has no in-release link -> construct it
                    rel.setdefault("tender", {}).setdefault("documents", []).append({"url": PORTAL.format(oc)})
                t, a = parse_release(rel, "AUS", self.name, cpv_by_hs, scraped_at)
                tenders += t
                awards += a
            url = (d.get("links") or {}).get("next")
            if not url:
                break
            time.sleep(self.pause)
        print(f"[au-tenders] {len(tenders)} tenders, {len(awards)} awards matched (AUS)")
        return tenders, awards

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
                print(f"[au-tenders] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
