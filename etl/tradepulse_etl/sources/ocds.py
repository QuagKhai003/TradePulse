"""
ocds.py — SHARED Open Contracting (OCDS) source: market-specific public buyers + awards for the many
          governments that publish the OCDS JSON standard (UK, Australia, Ukraine, South Africa, Chile,
          Moldova, Dominican Republic, Kenya, …). One parser, many countries.
@context  TED covers EU buyers only. OCDS is the common standard everywhere else. Unlike TED, these
          feeds have NO server-side product filter (proven: UK ignores keyword+cpvCodes) — so we page
          recent releases and match each one's CPV classification to our products LOCALLY (config.
          TENDER_CPV), the same CPV crosswalk TED uses. Each source is one country -> we tag its ISO3.
@golden   Buyer + supplier ORGANISATION + the official notice link only — never a contact person.
@warn     Bulk-paged: our products are niche, so most releases don't match. `max_pages` bounds the scan.
          `since` stops paging once releases pre-date the window (feeds are newest-first).
@limits   Network in _get only; parse_release + the matchers are pure/tested. CPV scheme only (a feed
          that classifies by UNSPSC/CPC needs its own crosswalk — flagged, not silently matched).
@affects  Rows share TED's shape -> db.upsert_tenders / upsert_awards -> tenders/awards-<hs>.json.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

_NOTICE_RE = re.compile(r"https?://[^\"\s]+/[Nn]otice/[0-9A-Za-z._%-]+")


def _stem(cpv: str) -> str:
    """CPV is hierarchical with trailing zeros — strip them so a child code matches its parent stem."""
    return cpv.rstrip("0") or cpv


# CPV-family schemes. Ukraine's ДК021 and Moldova's CPV are literal CPV codes, so they reuse our CPV
# crosswalk. (UNSPSC feeds — AU/CL/DO — carry a different code space and need a UNSPSC->HS crosswalk.)
_CPV_SCHEMES = ("CPV", "ДК021", "")


def _cpvs(rel: dict) -> set[str]:
    """Every CPV-family code on a release — the tender's classification + additionals + each item's, at
    both tender and (for feeds like AusTender) contract level."""
    out: set[str] = set()

    def add(c):
        if isinstance(c, dict) and c.get("id") and (c.get("scheme") or "").upper().replace("-", "") in \
                [s.upper().replace("-", "") for s in _CPV_SCHEMES]:
            out.add(str(c["id"]).split("-")[0])          # ДК021 codes carry a '-check' suffix; drop it

    def scan(container):
        c = container or {}
        add(c.get("classification"))
        for x in (c.get("additionalClassifications") or []):
            add(x)
        for it in (c.get("items") or []):
            add(it.get("classification"))
            for x in (it.get("additionalClassifications") or []):
                add(x)

    scan(rel.get("tender"))
    for con in (rel.get("contracts") or []):
        scan(con)
    return out


def _buyer_name(rel: dict) -> str | None:
    """Buyer org: top-level buyer, else tender.procuringEntity, else a party with a buyer role — the
    layouts the different national OCDS feeds actually use."""
    for cand in ((rel.get("buyer") or {}).get("name"),
                 ((rel.get("tender") or {}).get("procuringEntity") or {}).get("name")):
        if cand:
            return cand.strip()
    for p in (rel.get("parties") or []):
        roles = [r.lower() for r in (p.get("roles") or [])]
        if ("buyer" in roles or "procuringentity" in roles) and p.get("name"):
            return p["name"].strip()
    return None


def match_hs(cpvs: set[str], cpv_by_hs: dict[str, list[str]]) -> set[str]:
    """Products whose CPV stem is a prefix of any of the release's CPV codes."""
    hits: set[str] = set()
    for hs, prod_cpvs in cpv_by_hs.items():
        for pc in prod_cpvs:
            stem = _stem(pc)
            if any(str(c).startswith(stem) for c in cpvs):
                hits.add(hs)
                break
    return hits


def _source_url(rel: dict) -> str | None:
    """An openable link for the notice: a /notice/ URL, else a tender document/URL, else any http URL —
    different national feeds expose it differently. None -> the row is dropped (Golden Rule: cite source)."""
    blob = json.dumps(rel)
    m = _NOTICE_RE.search(blob)
    if m:
        return m.group(0)
    t = rel.get("tender") or {}
    for d in (t.get("documents") or []):
        if d.get("url"):
            return d["url"]
    for k in ("url", "urlTender"):
        if t.get(k):
            return t[k]
    m2 = re.search(r'https?://[^\"\s]{14,}', blob)
    return m2.group(0) if m2 else None


def parse_release(rel: dict, iso3: str, source: str, cpv_by_hs: dict[str, list[str]],
                  scraped_at: str) -> tuple[list[dict], list[dict]]:
    """One OCDS release -> (tender rows, award rows) for every product it matches. Empty if no match."""
    hits = match_hs(_cpvs(rel), cpv_by_hs)
    if not hits:
        return [], []
    t = rel.get("tender") or {}
    buyer = _buyer_name(rel)
    title = (t.get("title") or "").strip()
    url = _source_url(rel)
    if not (buyer and title and url):
        return [], []
    oid = str(rel.get("ocid") or rel.get("id") or "")
    pub = (rel.get("date") or "")[:10] or None
    deadline = ((t.get("tenderPeriod") or {}).get("endDate") or "")[:10] or None
    cpv = next(iter(_cpvs(rel)), "")
    tenders, awards = [], []
    for hs in hits:
        base = {"id": oid, "hs6": hs, "source": source, "cpv": cpv, "match_kind": "contract",
                "title": title, "buyer": buyer, "buyer_country": iso3, "url": url, "scraped_at": scraped_at}
        tenders.append({**base, "published": pub, "deadline": deadline})
        for a in (rel.get("awards") or []):
            val = a.get("value") or {}
            adate = (a.get("date") or "")[:10] or None
            for s in (a.get("suppliers") or []):
                name = (s.get("name") or "").strip()
                if name:
                    awards.append({**base, "winner": name, "winner_country": iso3, "award_date": adate,
                                   "value": val.get("amount"), "currency": val.get("currency"),
                                   "published": pub})
    return tenders, awards


class OcdsSource:
    def __init__(self, start_url: str, country_iso3: str, source_name: str,
                 timeout: int = 40, pause: float = 0.3, max_pages: int = 40):
        # start_url is the FULL first-page URL incl. query; a '{since}' placeholder is filled per pull
        # (for date-parameterised feeds like Scotland). Pagination then follows OCDS links.next.
        self.start_url = start_url
        self.country = country_iso3
        self.source_name = source_name
        self.timeout = timeout
        self.pause = pause
        self.max_pages = max_pages

    def pull(self, cpv_by_hs: dict[str, list[str]], since: str, scraped_at: str) -> tuple[list[dict], list[dict]]:
        """Page recent releases (newest first via links.next), match locally. `since` = 'YYYY-MM-DD'."""
        tenders: list[dict] = []
        awards: list[dict] = []
        url = self.start_url.format(since=since)
        for _ in range(self.max_pages):
            d = self._get(url)
            if not d:
                break
            rels = d.get("releases") or []
            oldest = None
            for rel in rels:
                t, a = parse_release(rel, self.country, self.source_name, cpv_by_hs, scraped_at)
                tenders += t
                awards += a
                oldest = (rel.get("date") or oldest) or oldest
            url = (d.get("links") or {}).get("next")
            if not url or (oldest and oldest[:10] < since):     # newest-first: past the window -> stop
                break
            time.sleep(self.pause)
        print(f"[{self.source_name}] {len(tenders)} tenders, {len(awards)} awards matched ({self.country})")
        return tenders, awards

    def _get(self, url: str) -> dict | None:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 tradepulse/0.1",
                                                   "Accept": "application/json"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 3:                 # rate-limited: honour Retry-After, back off
                    wait = int(e.headers.get("Retry-After") or 0) or (10 * (attempt + 1))
                    time.sleep(min(wait, 40))
                    continue
                if attempt < 3:
                    time.sleep(self.pause * 4)
                    continue
                print(f"[{self.source_name}] warn HTTP {e.code}")
                return None
            except Exception as e:  # noqa: BLE001 — transient; back off
                if attempt < 3:
                    time.sleep(self.pause * 4)
                    continue
                print(f"[{self.source_name}] warn {type(e).__name__}")
                return None
