"""
__main__.py — CLI entry: `python -m tradepulse_etl [--source fixture|comtrade]`.
@context  One command runs the whole batch (plan §10.3): pull -> trade_flows -> signals ->
          web snapshot. That single command is what makes the localhost app show data.
@done     Parses args; runs pipeline; computes + upserts signals; writes the web snapshot.
@limits   Thin CLI wrapper; logic lives in pipeline/signals/export. Supplies the clock (computed_at).
@affects  Calls pipeline.run + signals.compute_signals + export.write_snapshot.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from .db import DEFAULT_DB, connect, count_trade_flows, fetch_flows, upsert_signals
from .export import DEFAULT_SNAPSHOT, build_snapshot, write_snapshot
from .pipeline import get_source, run
from .signals import compute_signals


def main() -> None:
    ap = argparse.ArgumentParser(prog="tradepulse_etl", description="Build TradePulse Layer-1 data.")
    ap.add_argument("--source", default="fixture", choices=["fixture", "comtrade"],
                    help="data source (default: fixture — offline sample data)")
    ap.add_argument("--period", default="2025", help="period for the comtrade source")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite path")
    ap.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT), help="web snapshot output path")
    args = ap.parse_args()

    now_iso = datetime.now(timezone.utc).isoformat()
    conn = connect(args.db)

    n = run(get_source(args.source, period=args.period), conn)
    sigs = compute_signals(fetch_flows(conn), now_iso)
    upsert_signals(conn, sigs)
    snap = build_snapshot(conn, generated_at=now_iso)
    out = write_snapshot(snap, args.snapshot)

    print(f"[tradepulse] flows={count_trade_flows(conn)} (upserted {n}) signals={len(sigs)} "
          f"feed={len(snap['feed'])} snapshot={out}")


if __name__ == "__main__":
    main()
