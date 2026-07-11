"""
sourcing.py — build the quarterly partner-sourcing drill-down data (plan §7.3).
@context  For a few focus reporters, turn quarterly all-partner flows into: top partners (latest
          quarter share + YoY) + a per-quarter series for the stacked chart. One file per product,
          keyed by reporter. Separate from the global annual snapshot so that stays clean.
@done     build_sourcing(rows, hs6); write_sourcing().
@limits   PURE aggregation; no I/O except write_sourcing. Importer/exporter both flows.
@affects  Fed by ComtradeSource.pull_sourcing; consumed by web country page.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config
from .reference import country_name
from .signals import prev_year_period

TOP = 6


def _name_vi(code: int) -> str:
    return "Việt Nam" if code == config.PARTNER_VIETNAM else country_name(code)


def _flow_block(frows: list[dict]) -> dict | None:
    by_partner: dict[int, dict[str, float]] = {}
    for r in frows:
        by_partner.setdefault(r["partnerCode"], {})[r["period"]] = r["primaryValue"]
    world = by_partner.get(config.PARTNER_WORLD, {})
    periods = sorted(world.keys())
    if len(periods) < 2:
        return None
    latest = periods[-1]
    wl = world.get(latest) or 0

    latest_list = []
    for code, per in by_partner.items():
        if code == config.PARTNER_WORLD:
            continue
        v = per.get(latest)
        if v is None:
            continue
        base = per.get(prev_year_period(latest))
        yoy = ((v - base) / base) if (base and base > 0) else None
        latest_list.append({
            "code": code, "name_en": country_name(code), "name_vi": _name_vi(code),
            "value_usd": v, "share": (v / wl if wl else None),
            "yoy_delta": yoy, "direction": (None if yoy is None else ("up" if yoy >= 0 else "down")),
        })
    latest_list.sort(key=lambda p: p["value_usd"], reverse=True)

    top_codes = [p["code"] for p in latest_list[:TOP]]
    series = [{"code": c, "name_en": country_name(c), "name_vi": _name_vi(c),
               "values": [by_partner.get(c, {}).get(p, 0.0) for p in periods]} for c in top_codes]
    other = [max(0.0, world[p] - sum(by_partner.get(c, {}).get(p, 0.0) for c in top_codes)) for p in periods]
    if any(v > 0 for v in other):
        series.append({"code": -1, "name_en": "Other", "name_vi": "Khác", "values": other})
    return {"periods": periods, "partners": latest_list[:TOP], "series": series}


def build_sourcing(rows: list[dict], hs6: str) -> dict:
    rows = [r for r in rows if str(r["cmdCode"]) == hs6]
    by_rep: dict[int, dict[str, list]] = {}
    for r in rows:
        by_rep.setdefault(r["reporterCode"], {}).setdefault(r["flowCode"], []).append(r)

    out = {}
    for rep, byflow in by_rep.items():
        exp = _flow_block(byflow.get(config.FLOW_EXPORT, []))
        imp = _flow_block(byflow.get(config.FLOW_IMPORT, []))
        if exp or imp:
            out[str(rep)] = {"export": exp, "import": imp}
    return out


def write_sourcing(sourcing: dict, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sourcing, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
