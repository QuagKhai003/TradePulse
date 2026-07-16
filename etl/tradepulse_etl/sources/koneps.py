"""
koneps.py — South Korea public procurement (나라장터/KONEPS): market-specific public BUYERS (KR market).
@context  TED is EU-only; this is Korea's equivalent. KONEPS (조달청/Public Procurement Service) publishes
          every public bid notice: the demanding institution (수요기관 = the buyer), the title, an openable
          g2b.go.kr link, and the date. data.go.kr OpenAPI, keyed (KCS_SERVICE_KEY, provider 1230000 must
          be activated for the account). No server-side product filter -> we page recent notices by date
          and match the KOREAN title keywords locally (config.KONEPS_KW). Tagged KOR (M49 410).
@golden   Buyer ORGANISATION + the official notice link only — never a contact person.
@limits   Network in _get only. serviceKey goes RAW in the URL (already URL-encoded), like sources/kcs.py.
@affects  Rows share TED's tender shape -> db.upsert_tenders -> tenders-<hs>.json.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

BID = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoThng"


class KonepsSource:
    name = "koneps"

    def __init__(self, key: str | None = None, timeout: int = 40, pause: float = 0.4, max_pages: int = 12):
        self.key = key
        self.timeout = timeout
        self.pause = pause
        self.max_pages = max_pages

    def pull(self, kw_by_hs: dict[str, list[str]], since: str, until: str, scraped_at: str) -> list[dict]:
        """Page recent bid notices (`since`/`until` = 'YYYYMMDD'), match Korean title keywords -> KR tender
        rows. Returns [] with no key (data.go.kr provider 1230000 not activated)."""
        if not self.key:
            return []
        rows: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for page in range(1, self.max_pages + 1):
            data = self._get({"pageNo": str(page), "numOfRows": "100", "inqryDiv": "1",
                              "inqryBgnDt": since + "0000", "inqryEndDt": until + "2359", "type": "json"})
            items = (((data or {}).get("response") or {}).get("body") or {}).get("items")
            if not items:
                break
            items = items if isinstance(items, list) else [items]
            for it in items:
                row = self._notice(it, kw_by_hs, scraped_at)
                for r in row:
                    key = (r["id"], r["hs6"])
                    if key not in seen:
                        seen.add(key)
                        rows.append(r)
            if len(items) < 100:
                break
            time.sleep(self.pause)
        print(f"[koneps] {len(rows)} KR tender rows matched")
        return rows

    @staticmethod
    def _notice(it: dict, kw_by_hs: dict[str, list[str]], scraped_at: str) -> list[dict]:
        title = (it.get("bidNtceNm") or "").strip()
        buyer = (it.get("dminsttNm") or it.get("ntceInsttNm") or "").strip()
        url = (it.get("bidNtceDtlUrl") or "").strip()
        nid = (it.get("bidNtceNo") or "").strip()
        if not (title and buyer and url and nid):
            return []
        out = []
        for hs, kws in kw_by_hs.items():
            if any(kw in title for kw in kws):          # Korean substring match on the notice title
                out.append({
                    "id": nid, "hs6": hs, "source": "koneps", "cpv": (kws[0] if kws else ""),
                    "match_kind": "contract", "title": title,
                    "buyer": buyer, "buyer_country": "KOR",          # -> M49 410
                    "published": (str(it.get("bidNtceDt") or "")[:10]) or None,
                    "deadline": (str(it.get("bidClseDt") or "")[:10]) or None,
                    "url": url, "scraped_at": scraped_at,
                })
        return out

    def _get(self, params: dict) -> dict | None:
        url = f"{BID}?serviceKey={self.key}&" + urllib.parse.urlencode(params)   # key RAW (already encoded)
        req = urllib.request.Request(url, headers={"User-Agent": "tradepulse/0.1"})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — transient; back off once
                if attempt == 0:
                    time.sleep(self.pause * 4)
                    continue
                print(f"[koneps] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
