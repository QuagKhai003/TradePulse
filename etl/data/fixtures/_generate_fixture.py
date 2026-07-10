"""
_generate_fixture.py — one-off generator for pellets.json (SAMPLE data, not real figures).
@context  Produces the offline raw fixture the pipeline/tests/web run on, in Comtrade raw shape.
          Numbers are illustrative but shaped to exercise every signal band (surge, decline,
          moderate, below-floor) AND partner-level sourcing for the drill-down (Japan/Korea).
@limits   Dev tool. Not imported by the package. Deterministic (no clock/random).
@affects  Writes ./pellets.json.
"""
import json
from pathlib import Path

PERIODS = ["2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"]
PUBLISHED = ["2025-02-15", "2025-05-15", "2025-08-15", "2025-11-15", "2026-02-15", "2026-05-15"]

# World-partner (code 0) import totals per quarter, in MILLIONS USD. Shaped to hit each band:
#   JP surge/up (FIT)   KR significant decline (subsidy cut)   EU/GB moderate up   US below $10M floor
WORLD = {
    392: [500, 520, 540, 560, 600, 700],   # Japan
    410: [300, 320, 300, 290, 200, 150],   # South Korea
    97:  [900, 950, 980, 1000, 1050, 1150], # EU
    842: [6, 7, 8, 7, 9, 9.5],             # US (below floor)
    826: [200, 210, 205, 220, 235, 255],   # UK
}

# Partner mix (share of world) for the drill-down markets. Shares sum to 1.0 so partners == world.
PARTNERS = {
    392: {704: 0.55, 360: 0.20, 458: 0.10, 124: 0.08, 842: 0.07},   # VN, Indonesia, Malaysia, Canada, US
    410: {704: 0.40, 360: 0.35, 643: 0.15, 124: 0.10},              # VN, Indonesia, Russia, Canada
}


def rec(reporter, partner, i, value):
    value = round(value, 2)
    return {
        "reporterCode": reporter, "partnerCode": partner, "cmdCode": "440131",
        "period": PERIODS[i], "flowCode": "M", "primaryValue": value,
        "netWgt": round(value / 0.18), "qtyUnitAbbr": "kg", "publishedDate": PUBLISHED[i],
    }


records = []
for reporter, millions in WORLD.items():
    for i, m in enumerate(millions):
        records.append(rec(reporter, 0, i, m * 1_000_000))          # World aggregate
        for partner, share in PARTNERS.get(reporter, {}).items():
            records.append(rec(reporter, partner, i, m * 1_000_000 * share))

out = Path(__file__).with_name("pellets.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(records)} records -> {out}")
