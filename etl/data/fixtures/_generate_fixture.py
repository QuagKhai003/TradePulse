"""
_generate_fixture.py — one-off generator for pellets.json (SAMPLE data, not real figures).
@context  Produces the offline raw fixture the pipeline/tests/web run on, in Comtrade raw shape.
          Numbers are illustrative but shaped to exercise every signal band (surge, decline,
          moderate, and a below-floor cell). Re-run to regenerate; the JSON is the committed artifact.
@limits   Dev tool. Not imported by the package. Deterministic (no clock/random).
@affects  Writes ./pellets.json.
"""
import json
from pathlib import Path

PERIODS = ["2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"]
PUBLISHED = ["2025-02-15", "2025-05-15", "2025-08-15", "2025-11-15", "2026-02-15", "2026-05-15"]

# (reporterCode, partnerCode) -> value_usd per quarter in MILLIONS. Shaped to hit each band:
#   JP world  = surge/significant up (FIT-driven)      KR world = significant decline (subsidy cut)
#   EU/GB world = moderate up          US world = below the $10M floor (no signal)
SERIES = {
    (392, 0):   [500, 520, 540, 560, 600, 700],
    (410, 0):   [300, 320, 300, 290, 200, 150],
    (97, 0):    [900, 950, 980, 1000, 1050, 1150],
    (842, 0):   [6, 7, 8, 7, 9, 9.5],
    (826, 0):   [200, 210, 205, 220, 235, 255],
    (392, 704): [275, 286, 297, 308, 330, 385],
    (410, 704): [120, 128, 120, 116, 80, 60],
}

records = []
for (reporter, partner), millions in SERIES.items():
    for i, m in enumerate(millions):
        value = round(m * 1_000_000, 2)
        records.append({
            "reporterCode": reporter,
            "partnerCode": partner,
            "cmdCode": "440131",
            "period": PERIODS[i],
            "flowCode": "M",
            "primaryValue": value,
            "netWgt": round(value / 0.18),   # ~ $180/tonne -> kg
            "qtyUnitAbbr": "kg",
            "publishedDate": PUBLISHED[i],
        })

out = Path(__file__).with_name("pellets.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {len(records)} records -> {out}")
