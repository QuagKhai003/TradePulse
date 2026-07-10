"""
tradepulse_etl — the Python ETL package for TradePulse (Layer 1 trade flows + signals).
@context  Deterministic batch pipeline over free trade data (plan §10). Stdlib-only (no pip).
@affects  Run via `python -m tradepulse_etl` from the etl/ folder.
"""
__all__ = ["config", "db", "transform", "pipeline"]
