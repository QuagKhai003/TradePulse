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


def _index(rows: list[dict]) -> dict[int, dict[str, float]]:
    by: dict[int, dict[str, float]] = {}
    for r in rows:
        by.setdefault(r["partnerCode"], {})[r["period"]] = r["primaryValue"]
    return by


def _flow_block(table_rows: list[dict], chart_rows: list[dict]) -> dict | None:
    """The TABLE (top partners: value, share, YoY) is built from ANNUAL data — latest FULL YEAR value and
    a year-over-year change — so every product reads the same way. The CHART (series + periods) is built
    from chart_rows, which may be a finer grain (quarterly for the focus markets) or the same annual rows.
    Both use the SAME top partners (the annual ranking) so the chart legend matches the table."""
    t_by = _index(table_rows)
    t_world = t_by.get(config.PARTNER_WORLD, {})
    t_periods = sorted(t_world)
    if not t_periods:
        return None
    latest = t_periods[-1]
    wl = t_world.get(latest) or 0

    partners = []
    for code, per in t_by.items():
        if code == config.PARTNER_WORLD:
            continue
        v = per.get(latest)
        if v is None:
            continue
        base = per.get(prev_year_period(latest))          # prior YEAR — year over year
        yoy = ((v - base) / base) if (base and base > 0) else None
        partners.append({
            "code": code, "name_en": country_name(code), "name_vi": _name_vi(code),
            "value_usd": v, "share": (v / wl if wl else None),
            "yoy_delta": yoy, "direction": (None if yoy is None else ("up" if yoy >= 0 else "down")),
        })
    partners.sort(key=lambda p: p["value_usd"], reverse=True)
    partners = partners[:TOP]
    top_codes = [p["code"] for p in partners]

    c_by = _index(chart_rows)
    c_world = c_by.get(config.PARTNER_WORLD, {})
    c_periods = sorted(c_world)
    series = [{"code": c, "name_en": country_name(c), "name_vi": _name_vi(c),
               "values": [c_by.get(c, {}).get(p, 0.0) for p in c_periods]} for c in top_codes]
    other = [max(0.0, c_world[p] - sum(c_by.get(c, {}).get(p, 0.0) for c in top_codes)) for p in c_periods]
    if any(v > 0 for v in other):
        series.append({"code": -1, "name_en": "Other", "name_vi": "Khác", "values": other})
    return {"periods": c_periods, "partners": partners, "series": series}


def build_sourcing(annual_rows: list[dict], hs6: str, quarterly_rows: list[dict] | None = None) -> dict:
    """Table from `annual_rows` (always annual → uniform value + YoY). Chart from `quarterly_rows` when
    given (the focus markets' fresher trend), else from the annual rows (every other product)."""
    a = [r for r in annual_rows if str(r["cmdCode"]) == hs6]
    q = [r for r in (quarterly_rows or []) if str(r["cmdCode"]) == hs6]

    def group(rows):
        by: dict[int, dict[str, list]] = {}
        for r in rows:
            by.setdefault(r["reporterCode"], {}).setdefault(r["flowCode"], []).append(r)
        return by

    a_by, q_by = group(a), group(q)
    out = {}
    for rep, byflow in a_by.items():
        exp_a = byflow.get(config.FLOW_EXPORT, [])
        imp_a = byflow.get(config.FLOW_IMPORT, [])
        exp = _flow_block(exp_a, q_by.get(rep, {}).get(config.FLOW_EXPORT) or exp_a)
        imp = _flow_block(imp_a, q_by.get(rep, {}).get(config.FLOW_IMPORT) or imp_a)
        if exp or imp:
            out[str(rep)] = {"export": exp, "import": imp}
    return out


def total_quarterly_flows(sourcing: dict, hs6: str, now_iso: str) -> list[dict]:
    """Reconstruct each focus reporter's all-commodities QUARTERLY total (the World-partner value) from a
    built sourcing map, as trade_flow rows. TOTAL is excluded from the heavy all-reporter quarterly pull
    (config: the all-commodity monthly payload is too big), so the headline TOTAL figure is annual-only
    and the Year/Quarter toggle greys out on the 'all products' view. But the sourcing drill-down we
    ALREADY fetched for the focus reporters carries the quarters — and the World total per period equals
    the sum of the stacked series (top partners + 'Other'), by construction. Promoting that into
    trade_flows (partner=World, freq='Q') gives build_snapshot a quarterly slot with NO extra network.
    @limits  Focus reporters only (the only ones with quarterly sourcing); quarterly periods only."""
    flow_by_key = {"export": config.FLOW_EXPORT, "import": config.FLOW_IMPORT}
    out: list[dict] = []
    pub = now_iso[:10]
    for rep, blocks in sourcing.items():
        for key, flow in flow_by_key.items():
            blk = (blocks or {}).get(key)
            if not blk:
                continue
            periods = blk.get("periods") or []
            series = blk.get("series") or []
            for i, period in enumerate(periods):
                if "Q" not in period:                          # quarterly grain only
                    continue
                world = sum((s["values"][i] if i < len(s.get("values", [])) else 0.0) for s in series)
                if world <= 0:
                    continue
                out.append({
                    "reporter": int(rep), "partner": config.PARTNER_WORLD, "hs6": hs6,
                    "period": period, "freq": "Q", "flow": flow, "value_usd": world,
                    "quantity": None, "qty_unit": None, "source": "comtrade", "published_date": pub,
                })
    return out


def write_sourcing(sourcing: dict, path: Path | str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sourcing, ensure_ascii=False, indent=1), encoding="utf-8")
    return path
