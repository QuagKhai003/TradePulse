"""
_gen_countries.py — one-off: fetch Comtrade REPORTER + PARTNER reference -> bundled code->name map.
@context  /data rows carry only numeric M49 codes — reporterCode for a country's own flows, partnerCode
          for its trading partners. This bundles code -> English name + ISO-alpha3 so the ETL needs no
          network for names and the map can match world-atlas. PARTNER areas are merged in because a
          country's partners include Comtrade's "nes"/aggregate codes (490 "Other Asia, nes", 899
          "Areas, nes", 838 "Free Zones", ...) that NEVER appear as reporters — without them a partner
          row in the sourcing table shows a bare number (e.g. "490") instead of a name.
@limits   Dev tool; run occasionally. Reporters win on conflict (authoritative names + the ISO3 the map
          needs for real countries); partners only fill codes reporters don't have.
"""
import json
import urllib.request
from pathlib import Path


def _fetch(url, code_key, desc_key, iso_key):
    req = urllib.request.Request(url, headers={"User-Agent": "tradepulse/0.1"})
    rows = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())["results"]
    out = {}
    for r in rows:
        if r.get("isGroup"):                       # skip aggregates (World, EU-27, ...)
            continue
        code = r.get(code_key)
        if code in (None, "all", 0, "0"):
            continue
        name = (r.get(desc_key) or r.get("text") or "").strip()
        if not name:
            continue
        out[str(code)] = {"name": name, "iso3": (r.get(iso_key) or "").strip() or None}
    return out


partners = _fetch("https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json",
                  "PartnerCode", "PartnerDesc", "PartnerCodeIsoAlpha3")
reporters = _fetch("https://comtradeapi.un.org/files/v1/app/reference/Reporters.json",
                   "reporterCode", "reporterDesc", "reporterCodeIsoAlpha3")
merged = {**partners, **reporters}   # reporters override: real countries keep their ISO3 for the map

path = Path(__file__).with_name("countries.json")
path.write_text(json.dumps(merged, ensure_ascii=False, indent=0), encoding="utf-8")
print(f"wrote {len(merged)} countries ({len(partners)} partner + {len(reporters)} reporter) -> {path}")
