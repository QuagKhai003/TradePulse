"""
_gen_cpv.py — build reference/cpv_by_hs.json: the HS4 -> CPV map that gives every product a tender feed.
@context  TED classifies by CPV, not HS, and no official HS<->CPV crosswalk exists. So we PROPOSE a
          mapping by matching each HS heading's English text against the CPV 2008 label list, then
          VERIFY every proposal live against TED: a CPV is kept only if it actually returns notices
          whose MAIN classification (contract or lot) is that code. A text match that returns nothing
          real is dropped — verification, not similarity, is what makes it into the file.
@warn     The proposal step is a heuristic; the verification step is the guarantee. Wrong-but-plausible
          text matches (e.g. an HS heading whose words appear in an unrelated CPV label) survive only if
          TED really files notices under that code for that product — and the UI always shows the CPV
          code + the official notice link, so a bad row is traceable to its source.
@limits   Regenerate by hand (network + ~30 min); the OUTPUT is committed and reviewable. Not imported
          at runtime — config.py just reads the JSON.
@affects  Writes reference/cpv_by_hs.json, consumed by config.TENDER_CPV.
Run: python -m tradepulse_etl.reference._gen_cpv
"""
from __future__ import annotations

import csv
import io
import json
import re
import time
import urllib.request
from pathlib import Path

# CPV 2008 code + English label. Mirror of the official list published at ted.europa.eu/en/simap/cpv
# (the EU's own download handler 403s to scripts). Provenance does not have to be trusted: every code
# we keep is verified against the live TED API below, and the app shows the code + notice link.
CPV_CSV = ("https://raw.githubusercontent.com/chemaar/moldeas2/master/apps/moldeas-transformer/"
           "src/main/resources/cpv/cpv-codes-2008-2003.csv")
TED_API = "https://api.ted.europa.eu/v3/notices/search"
OUT = Path(__file__).with_name("cpv_by_hs.json")

# CPV divisions that are GOODS a factory could supply. Services/works (45=construction, 50=repair,
# 60=transport, 71=engineering, 79=business services...) are not export leads — a CPV match landing
# there is a false positive by construction, so they never enter the candidate pool.
GOODS_DIVISIONS = {"03", "09", "14", "15", "16", "18", "19", "22", "24", "30", "31", "32", "33",
                   "34", "35", "37", "38", "39", "42", "43", "44", "48"}

# HS chapter -> the CPV divisions that chapter's goods can legitimately live in. This is the guard that
# makes text matching safe: without it "Cashew nuts" matches CPV 44531600 (fastener NUTS, i.e. bolts)
# and "Tea" matches "Flavoured yoghurt". A word can be shared across domains; a domain cannot.
CHAPTER_DIVISIONS = {
    **{c: {"03", "15"} for c in range(1, 15)},      # 01-14 animals, plants, vegetables
    15: {"15", "24"},                                # fats & oils
    **{c: {"15"} for c in range(16, 25)},           # 16-24 food, beverages, tobacco
    **{c: {"09", "14"} for c in range(25, 28)},         # 25-27 minerals, fuels (NOT 44: a
                                                        #   fuel is not a construction material)
    **{c: {"24", "33", "38"} for c in range(28, 39)},   # 28-38 chemicals, pharma
    39: {"19", "44"}, 40: {"19", "34"},             # plastics, rubber
    **{c: {"18", "19"} for c in range(41, 44)},     # leather, fur
    **{c: {"03", "44", "39"} for c in range(44, 47)},   # 44-46 wood, cork, basketware
    **{c: {"22", "30", "44"} for c in range(47, 50)},   # 47-49 paper, printed matter
    **{c: {"18", "19", "39"} for c in range(50, 64)},   # 50-63 textiles, apparel
    **{c: {"18"} for c in range(64, 68)},           # 64-67 footwear, headgear
    **{c: {"14", "44", "39"} for c in range(68, 71)},   # 68-70 stone, ceramics, glass
    71: {"14", "18"},                                # pearls, precious metals
    **{c: {"14", "44"} for c in range(72, 84)},     # 72-83 base metals
    84: {"16", "30", "42", "43"},                    # machinery
    85: {"31", "32", "48"},                          # electrical, electronics
    **{c: {"34"} for c in range(86, 90)},           # 86-89 vehicles, aircraft, ships
    **{c: {"33", "38"} for c in range(90, 93)},     # 90-92 instruments, clocks
    93: {"35"},                                      # arms
    **{c: {"39", "37"} for c in range(94, 97)},     # 94-96 furniture, toys, misc
    97: {"37"},                                      # works of art
}


def _allowed(hs: str) -> set[str]:
    """CPV divisions this HS heading may match in. Unknown chapter -> no match (safer than a wrong one)."""
    try:
        return CHAPTER_DIVISIONS.get(int(str(hs)[:2]), set())
    except ValueError:
        return set()

STOP = {"other", "than", "whether", "not", "or", "and", "of", "the", "for", "in", "with", "any",
        "form", "forms", "including", "excluding", "used", "new", "parts", "articles", "products",
        "preparations", "prepared", "fresh", "chilled", "frozen", "dried", "n.e.s", "nes", "kind",
        "kinds", "similar", "such", "their", "goods", "material", "materials", "related", "misc",
        "miscellaneous", "equipment", "machines", "machinery", "apparatus", "appliances"}


def _words(s: str) -> list[str]:
    return [w for w in re.split(r"[^a-z]+", (s or "").lower()) if len(w) > 2 and w not in STOP]


def _head(name: str) -> list[str]:
    """The HS heading's LEADING clause — 'Tea, whether or not flavoured' -> ['tea']. The head noun is
    what the heading is about; everything after the comma is qualification."""
    return _words(re.split(r"[,;(]", name or "")[0]) or _words(name)


def load_cpv() -> list[tuple[str, str]]:
    req = urllib.request.Request(CPV_CSV, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        text = r.read().decode("utf-8", "replace")
    out = []
    for row in csv.reader(io.StringIO(text), delimiter=";"):
        if len(row) < 2 or not row[0].strip().isdigit():
            continue
        code = row[0].strip().zfill(8)[:8]
        if code[:2] in GOODS_DIVISIONS:
            out.append((code, row[1].strip().rstrip(".")))
    return out


def propose(hs: str, hs_name: str, cpv: list[tuple[str, str]]) -> tuple[str, str, float] | None:
    """Best CPV for one HS heading. Three guards: the CPV must sit in a division this HS CHAPTER can
    legitimately use, the heading's HEAD noun must appear in the CPV label (a shared qualifier like
    'dried' is not a match), and the most specific code wins."""
    allowed = _allowed(hs)
    if not allowed:
        return None
    head = set(_head(hs_name))
    if not head:
        return None
    body = set(_words(hs_name))
    best = None
    for code, label in cpv:
        if code[:2] not in allowed:                     # wrong domain -> cannot be this product
            continue
        lab = set(_words(label))
        if not lab or not (head & lab):                 # head noun MUST appear
            continue
        overlap = len(body & lab) / max(1, len(lab))    # how much of the CPV label the HS covers
        head_cov = len(head & lab) / len(head)          # how much of the head noun is covered
        score = round(0.6 * head_cov + 0.4 * overlap, 3)
        specificity = len(code.rstrip("0"))             # 15863000 (tea) beats 15000000 (food)
        if score >= 0.6 and (best is None or (score, specificity) > (best[2], len(best[0].rstrip("0")))):
            best = (code, label, score)
    return best


def verify(code: str, session_pause: float = 0.6) -> int:
    """Live check: how many notices in the last year are ACTUALLY about this code (main cpv of the
    contract or of a lot)? Zero -> the proposal is dropped, however good the text match looked."""
    body = {"query": f"classification-cpv IN ({code}) AND publication-date>=20250101",
            "fields": ["publication-number", "main-classification-proc", "main-classification-lot"],
            "page": 1, "limit": 50, "scope": "ALL"}
    req = urllib.request.Request(TED_API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "tradepulse/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
    except Exception:
        return 0
    finally:
        time.sleep(session_pause)
    stem = code.rstrip("0") or code
    real = 0
    for n in data.get("notices") or []:
        codes = (n.get("main-classification-proc") or []) + (n.get("main-classification-lot") or [])
        if any(str(c).startswith(stem) for c in codes):
            real += 1
    return real


def main() -> None:
    from .. import config
    cpv = load_cpv()
    print(f"[cpv] {len(cpv)} goods CPV codes loaded")

    proposals: dict[str, tuple[str, str, float]] = {}
    for hs, p in config.PRODUCTS.items():
        if hs == "TOTAL":
            continue
        best = propose(hs, p["name_en"], cpv)
        if best:
            proposals[hs] = best
    print(f"[cpv] {len(proposals)} of {len(config.PRODUCTS)} products got a text match — verifying live")

    seen: dict[str, int] = {}
    out: dict[str, dict] = {}
    for i, (hs, (code, label, score)) in enumerate(sorted(proposals.items()), 1):
        if code not in seen:
            seen[code] = verify(code)
        n = seen[code]
        if n > 0:
            out[hs] = {"cpv": [code], "label": label, "score": score, "verified_notices": n}
        if i % 50 == 0:
            print(f"[cpv]   {i}/{len(proposals)} checked, {len(out)} kept")

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"[cpv] WROTE {OUT.name}: {len(out)} products with a VERIFIED tender feed "
          f"({len(proposals) - len(out)} text matches dropped — TED files nothing real under them)")


if __name__ == "__main__":
    main()
