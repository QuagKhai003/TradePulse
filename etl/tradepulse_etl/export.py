"""
export.py — build the web snapshot JSON from the DB (the web/ETL seam).
@context  The Next.js app reads a generated JSON snapshot, not the SQLite file directly (keeps
          `npm install` pure-JS on Windows; a documented swap to a real API later). One file =
          everything Layer 1 + the drill-down need: per-market value/band/history/VN-share/feed,
          plus partner sourcing (shares + YoY + per-quarter series) for covered markets.
@done     build_snapshot(conn, generated_at); write_snapshot(). Honest labels travel with the data.
@todo     Add export/import both sides + more products as verticals grow.
@limits   Serialisation only; signal math is in signals.py. generated_at passed in.
@affects  Reads trade_flows + signals. Writes web/public/data/snapshot.json (gitignored artifact).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config
from .signals import prev_year_period

BAND_RANK = {"surge": 0, "collapse": 0, "significant": 1, "moderate": 2, "new": 3}
DEFAULT_SNAPSHOT = Path(__file__).resolve().parents[2] / "web" / "public" / "data" / "snapshot.json"
TOP_PARTNERS = 5


def build_snapshot(conn, generated_at: str, hs6: str = "440131", flow: str = config.FLOW_IMPORT) -> dict:
    flows = [r for r in _flows(conn, flow) if r["hs6"] == hs6]
    world = [r for r in flows if r["partner"] == config.PARTNER_WORLD]
    signals = {(s["reporter"], s["period"]): s for s in _signals(conn, hs6, flow)}
    latest = max((r["period"] for r in world), default=None)
    sources = {r["source"] for r in world}

    markets = []
    for slug, meta in config.MARKETS.items():
        rep = meta["reporter"]
        series = sorted([r for r in world if r["reporter"] == rep], key=lambda r: r["period"])
        if not series:
            continue
        cur = series[-1]
        sig = signals.get((rep, cur["period"]))
        world_by_period = {r["period"]: r["value_usd"] for r in series}
        part_rows = [r for r in flows if r["reporter"] == rep and r["partner"] != config.PARTNER_WORLD]
        partners, sourcing = _partners(part_rows, world_by_period, cur["period"])
        vn = next((p for p in partners if p["code"] == config.PARTNER_VIETNAM), None)

        markets.append({
            "slug": slug, "reporter": rep,
            "name_en": meta["name_en"], "name_vi": meta["name_vi"],
            "period": cur["period"], "published_date": cur["published_date"],
            "value_usd": cur["value_usd"], "quantity": cur["quantity"], "qty_unit": cur["qty_unit"],
            "yoy_delta": (sig["yoy_delta"] if sig else None),
            "band": (sig["band"] if sig else "none"),
            "direction": (_direction(sig["yoy_delta"]) if sig and sig["band"] != "new" else None),
            "vn_share": (vn["share"] if vn else None),
            "history": [{"period": r["period"], "value_usd": r["value_usd"]} for r in series],
            "partners": partners,        # latest-period shares (may be [])
            "sourcing": sourcing,        # {periods, series} for the chart (or None)
        })

    feed = sorted([m for m in markets if m["band"] in BAND_RANK],
                  key=lambda m: (BAND_RANK[m["band"]], -m["value_usd"]))
    product = config.PRODUCTS.get(hs6, {"name_en": hs6, "name_vi": hs6})
    return {
        "generated_at": generated_at,
        "hs6": hs6, "product": product, "flow": flow,
        "latest_period": latest, "is_sample": ("fixture" in sources), "sources": sorted(sources),
        "markets": markets, "feed": feed,
    }


def _partners(part_rows, world_by_period, latest):
    """Return (latest_shares[], sourcing{periods,series}) for one market. Importer-reported."""
    if not part_rows:
        return [], None
    by_code: dict[int, dict[str, float]] = {}
    for r in part_rows:
        by_code.setdefault(r["partner"], {})[r["period"]] = r["value_usd"]

    world_latest = world_by_period.get(latest) or 0
    latest_list = []
    for code, per in by_code.items():
        val = per.get(latest)
        if val is None:
            continue
        base = per.get(prev_year_period(latest))
        yoy = ((val - base) / base) if (base and base > 0) else None
        latest_list.append({
            "code": code,
            "name_en": _cname(code, "en"), "name_vi": _cname(code, "vi"),
            "value_usd": val,
            "share": (val / world_latest) if world_latest else None,
            "yoy_delta": yoy,
            "direction": (_direction(yoy) if yoy is not None else None),
        })
    latest_list.sort(key=lambda p: p["value_usd"], reverse=True)

    # Sourcing series: top-N partners over every period (+ "Other" = world - sum(top-N)).
    periods = sorted(world_by_period.keys())
    top_codes = [p["code"] for p in latest_list[:TOP_PARTNERS]]
    series = [{
        "code": c, "name_en": _cname(c, "en"), "name_vi": _cname(c, "vi"),
        "values": [by_code.get(c, {}).get(p, 0.0) for p in periods],
    } for c in top_codes]
    other = [max(0.0, (world_by_period[p] - sum(by_code.get(c, {}).get(p, 0.0) for c in top_codes)))
             for p in periods]
    if any(v > 0 for v in other):
        series.append({"code": -1, "name_en": "Other", "name_vi": "Khác", "values": other})
    return latest_list, {"periods": periods, "series": series}


def write_snapshot(snapshot: dict, path: Path | str = DEFAULT_SNAPSHOT) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _direction(yoy: float) -> str:
    return "up" if yoy >= 0 else "down"


def _cname(code: int, lang: str) -> str:
    return config.COUNTRY_NAMES.get(code, {}).get(lang, str(code))


def _flows(conn, flow):
    from .db import fetch_flows
    return fetch_flows(conn, flow)


def _signals(conn, hs6, flow):
    return [dict(r) for r in conn.execute(
        "SELECT * FROM signals WHERE hs6=? AND flow=?", (hs6, flow)).fetchall()]
