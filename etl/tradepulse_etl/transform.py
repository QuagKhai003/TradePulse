"""
transform.py — raw source record -> trade_flows row.
@context  The single normalisation step between raw pulls and the star schema. Keeping it pure
          makes the pipeline reproducible: same raw in -> same rows out (plan §10.4).
@done     transform_record(); transform_all(). Coerces types, carries source + published_date.
@limits   PURE: no I/O, no network, no clock. Deterministic.
@affects  Input: raw dicts from sources. Output: rows for db.upsert_trade_flows.
"""
from __future__ import annotations


def transform_record(raw: dict, source_name: str) -> dict:
    return {
        "reporter": int(raw["reporterCode"]),
        "partner": int(raw["partnerCode"]),
        "hs6": str(raw["cmdCode"]),
        "period": str(raw["period"]),
        "flow": str(raw["flowCode"]),
        "value_usd": float(raw["primaryValue"]),
        "quantity": (float(raw["netWgt"]) if raw.get("netWgt") is not None else None),
        "qty_unit": raw.get("qtyUnitAbbr"),
        "source": source_name,
        "published_date": raw.get("publishedDate"),
    }


def transform_all(raw_records: list[dict], source_name: str) -> list[dict]:
    return [transform_record(r, source_name) for r in raw_records]
