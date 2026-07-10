"""
export.py — build the web snapshot JSON from the DB (the web/ETL seam).
@context  The Next.js app reads a generated JSON snapshot, not the SQLite file directly (keeps
          `npm install` pure-JS on Windows; a documented swap to a real API later). One file =
          everything Layer-1 needs: per-market latest value + YoY band + history + VN share + feed.
@done     build_snapshot(conn, generated_at); write_snapshot(). Honest labels (period, published,
          is_sample) travel with the data (plan §5 honest timestamps, §4.2 value/volume only).
@todo     Add per-market export/import both sides + more products as verticals grow.
@limits   Serialisation only; no signal math here (that's signals.py). generated_at passed in.
@affects  Reads trade_flows + signals. Writes web/public/data/snapshot.json (gitignored artifact).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config

# Feed shows moderate+ only (plan §7.1), ranked by severity then value.
BAND_RANK = {"surge": 0, "collapse": 0, "significant": 1, "moderate": 2, "new": 3}
DEFAULT_SNAPSHOT = Path(__file__).resolve().parents[2] / "web" / "public" / "data" / "snapshot.json"


def _latest_period(rows: list[dict]) -> str | None:
    return max((r["period"] for r in rows), default=None)  # 'YYYY-Qn' sorts lexically


def build_snapshot(conn, generated_at: str, hs6: str = "440131", flow: str = config.FLOW_IMPORT) -> dict:
    world = [r for r in _flows(conn, flow) if r["partner"] == config.PARTNER_WORLD and r["hs6"] == hs6]
    vietnam = {r["reporter"]: r for r in _flows(conn, flow)
               if r["partner"] == config.PARTNER_VIETNAM and r["hs6"] == hs6 and _is_latest(r, world)}
    signals = {(s["reporter"], s["period"]): s for s in _signals(conn, hs6, flow)}
    latest = _latest_period(world)
    sources = {r["source"] for r in world}

    markets = []
    for slug, meta in config.MARKETS.items():
        rep = meta["reporter"]
        series = sorted([r for r in world if r["reporter"] == rep], key=lambda r: r["period"])
        if not series:
            continue
        cur = series[-1]
        sig = signals.get((rep, cur["period"]))
        vn = vietnam.get(rep)
        vn_share = (vn["value_usd"] / cur["value_usd"]) if (vn and cur["value_usd"]) else None
        markets.append({
            "slug": slug, "reporter": rep,
            "name_en": meta["name_en"], "name_vi": meta["name_vi"],
            "period": cur["period"], "published_date": cur["published_date"],
            "value_usd": cur["value_usd"], "quantity": cur["quantity"], "qty_unit": cur["qty_unit"],
            "yoy_delta": (sig["yoy_delta"] if sig else None),
            "band": (sig["band"] if sig else "none"),
            "direction": (_direction(sig["yoy_delta"]) if sig and sig["band"] != "new" else None),
            "vn_share": vn_share,
            "history": [{"period": r["period"], "value_usd": r["value_usd"]} for r in series],
        })

    feed = sorted(
        [m for m in markets if m["band"] in BAND_RANK],
        key=lambda m: (BAND_RANK[m["band"]], -m["value_usd"]),
    )
    product = config.PRODUCTS.get(hs6, {"name_en": hs6, "name_vi": hs6})
    return {
        "generated_at": generated_at,
        "hs6": hs6, "product": product, "flow": flow,
        "latest_period": latest,
        "is_sample": ("fixture" in sources),
        "sources": sorted(sources),
        "markets": markets,
        "feed": feed,
    }


def write_snapshot(snapshot: dict, path: Path | str = DEFAULT_SNAPSHOT) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _direction(yoy: float) -> str:
    return "up" if yoy >= 0 else "down"


def _is_latest(row: dict, world: list[dict]) -> bool:
    return row["period"] == _latest_period([w for w in world if w["reporter"] == row["reporter"]])


def _flows(conn, flow):
    from .db import fetch_flows
    return fetch_flows(conn, flow)


def _signals(conn, hs6, flow):
    return [dict(r) for r in conn.execute(
        "SELECT * FROM signals WHERE hs6=? AND flow=?", (hs6, flow)).fetchall()]
