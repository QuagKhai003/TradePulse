"""
usaspending.py — US federal procurement AWARDS: market-specific PAST ORDERS + public buyers (US market).
@context  TED covers EU buyers only, so a non-EU country page showed EU buyers (wrong). This is the US
          equivalent: USAspending publishes every awarded federal contract — the awarding AGENCY (the
          public buyer) + the RECIPIENT (the supplier/seller) + amount + an openable award page. Keyless.
          Server-side full-text `keywords` filter, so — unlike the OCDS feeds — we can query per product.
@warn     Keyword search is broad: "coffee" can match a catering contract. match_kind stays 'contract'
          (USAspending has no CPV/lot structure); the product keyword is recorded in `cpv` for provenance.
@golden   Buyer + supplier ORGANISATIONS + the official award link only — never a contact person.
@limits   Network in _post only. USA-tagged (buyer_country/winner_country = 'USA' -> M49 842 downstream).
@affects  Stored via db.upsert_awards (same shape as TED awards); exported to awards-<hs>.json.
"""
from __future__ import annotations

import json
import time
import urllib.request

API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
AWARD_URL = "https://www.usaspending.gov/award/{}"
# A,B,C,D = the contract award types (definitive contracts, purchase orders, delivery orders, BPA calls).
AWARD_TYPES = ["A", "B", "C", "D"]
FIELDS = ["Award ID", "Recipient Name", "Awarding Agency", "Award Amount", "Description",
          "Start Date", "generated_internal_id"]


class UsaSpendingSource:
    name = "usaspending"

    def __init__(self, timeout: int = 60, pause: float = 0.4, page_size: int = 60):
        self.timeout = timeout
        self.pause = pause
        self.page_size = page_size

    def pull_awards(self, kw_by_hs: dict[str, list[str]], since: str, until: str,
                    scraped_at: str) -> list[dict]:
        """`since`/`until` = 'YYYY-MM-DD'. One full-text search per (product, keyword) -> US award rows."""
        rows: list[dict] = []
        seen: set[tuple[str, str]] = set()          # (award id, hs) — dedupe across keywords
        for hs6, kws in kw_by_hs.items():
            for kw in kws:
                body = {"filters": {"keywords": [kw], "award_type_codes": AWARD_TYPES,
                                    "time_period": [{"start_date": since, "end_date": until}]},
                        "fields": FIELDS, "limit": self.page_size, "page": 1}
                for r in (self._post(body) or {}).get("results", []) or []:
                    row = self._award(r, hs6, kw, scraped_at)
                    if not row:
                        continue
                    key = (row["id"], hs6)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append(row)
                time.sleep(self.pause)
        return rows

    @staticmethod
    def _award(r: dict, hs6: str, kw: str, scraped_at: str) -> dict | None:
        gid = r.get("generated_internal_id")
        agency = (r.get("Awarding Agency") or "").strip()
        if not gid or not agency:
            return None
        amt = r.get("Award Amount")
        try:
            value = float(amt) if amt not in (None, "") else None
        except (TypeError, ValueError):
            value = None
        desc = (r.get("Description") or "").strip()
        title = (desc[:140] or f"{kw} — {r.get('Award ID') or gid}")
        return {
            "id": str(gid),
            "hs6": hs6,
            "source": "usaspending",
            "cpv": kw,                               # the product keyword that matched (provenance)
            "match_kind": "contract",
            "title": title,
            "buyer": agency,                         # the US federal agency = the public buyer
            "buyer_country": "USA",                  # -> M49 842 via export._m49
            "winner": (r.get("Recipient Name") or "").strip() or None,   # the supplier/seller
            "winner_country": "USA",
            "award_date": (str(r.get("Start Date") or "")[:10]) or None,
            "value": value,
            "currency": "USD",
            "published": (str(r.get("Start Date") or "")[:10]) or None,
            "url": AWARD_URL.format(gid),
            "scraped_at": scraped_at,
        }

    def _post(self, body: dict) -> dict | None:
        req = urllib.request.Request(
            API, data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "tradepulse/0.1"})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001 — transient; back off once
                if attempt == 0:
                    time.sleep(self.pause * 4)
                    continue
                print(f"[usaspending] warn {type(e).__name__}:{getattr(e, 'code', '')}")
                return None
