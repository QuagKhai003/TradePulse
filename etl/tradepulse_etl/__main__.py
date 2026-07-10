"""
__main__.py — CLI entry: `python -m tradepulse_etl [--source fixture|comtrade]`.
@context  One command to (re)build trade_flows from a source into the SQLite DB (plan §10.3).
@done     Parses --source/--db; runs the pipeline; prints a row count.
@todo     Chain signal compute + web snapshot export here in batch 1.2.
@limits   Thin CLI wrapper; no logic of its own.
@affects  Calls pipeline.run + db.connect.
"""
from __future__ import annotations

import argparse

from .db import DEFAULT_DB, connect, count_trade_flows
from .pipeline import get_source, run


def main() -> None:
    ap = argparse.ArgumentParser(prog="tradepulse_etl", description="Load trade flows into SQLite.")
    ap.add_argument("--source", default="fixture", choices=["fixture", "comtrade"],
                    help="data source (default: fixture — offline sample data)")
    ap.add_argument("--period", default="2025", help="period for the comtrade source")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="SQLite path")
    args = ap.parse_args()

    conn = connect(args.db)
    source = get_source(args.source, period=args.period)
    n = run(source, conn)
    total = count_trade_flows(conn)
    print(f"[tradepulse] source={source.name} upserted={n} trade_flows_total={total} db={args.db}")


if __name__ == "__main__":
    main()
