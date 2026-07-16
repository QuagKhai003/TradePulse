"""
reference — bundled Comtrade reference data (country code -> name/ISO).
@context  The /data rows carry only numeric reporterCode; this maps them to names for the UI and
          to world-atlas ISO ids for the map. Regenerate with _gen_countries.py.
"""
import json
from pathlib import Path

_COUNTRIES = json.loads((Path(__file__).with_name("countries.json")).read_text(encoding="utf-8"))


def country_name(code) -> str:
    return (_COUNTRIES.get(str(code)) or {}).get("name") or str(code)


def country_iso3(code) -> str | None:
    return (_COUNTRIES.get(str(code)) or {}).get("iso3")


# A few ISO3 codes map to several M49 numbers (a current code + historical/aggregate variants — e.g. USA
# is 840 "United States of America", 841 "USA and Puerto Rico (...1980)", 842 "USA"). Pin the code our
# TRADE data actually uses (the Comtrade reporter code) so a buyer/seller country resolves to the right
# country page instead of a historical dead code.
_ISO3_M49_OVERRIDE = {"USA": 842}


def m49_by_iso3() -> dict[str, int]:
    """ISO3 -> numeric M49. Procurement sources give a buyer's country as ISO3; our flows key by M49.
    Skips historical/aggregate name variants so the current code wins; overrides pin the ambiguous ones."""
    out: dict[str, int] = {}
    for k, v in _COUNTRIES.items():
        iso, name = v.get("iso3"), v.get("name") or ""
        if not (iso and k.isdigit()):
            continue
        if any(t in name for t in ("(", "…", "Fmr", "former", ", nes")):   # historical/aggregate variant
            continue
        out[iso] = int(k)
    out.update(_ISO3_M49_OVERRIDE)
    return out
