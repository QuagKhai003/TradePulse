"""
base.py — the trade-data source seam.
@context  Every external data dependency sits behind an interface with a local impl now and a
          documented production swap later (CONVENTIONS §11). Callers depend on TradeSource,
          never on Comtrade specifics.
@done     TradeSource protocol: pull() returns RAW records (Comtrade-shaped dicts).
@todo     Add national-source impls (e-Stat, K-stat) as covered markets grow.
@limits   Interface only. No network here.
@affects  Implemented by fixture.py + comtrade.py; consumed by pipeline.py.
"""
from __future__ import annotations

from typing import Protocol


class TradeSource(Protocol):
    """Returns raw, untransformed records — raw-before-transform (plan §10.4)."""

    name: str

    def pull(self, hs_codes: list[str], reporters: list[int], partners: list[int]) -> list[dict]:
        """Raw records for the given HS codes x reporters x partners (quarterly, import flow)."""
        ...
