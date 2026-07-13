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


def m49_by_iso3() -> dict[str, int]:
    """ISO3 -> numeric M49. TED gives a buyer's country as ISO3; our flows key countries by M49."""
    return {v["iso3"]: int(k) for k, v in _COUNTRIES.items() if v.get("iso3") and k.isdigit()}
