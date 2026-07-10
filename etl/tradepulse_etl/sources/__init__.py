"""
sources — the trade-data source seam (base) + its impls (fixture, comtrade).
@context  Import point so callers do `from tradepulse_etl.sources import FixtureSource`.
@affects  Used by pipeline.get_source().
"""
from .base import TradeSource
from .comtrade import ComtradeSource
from .fixture import FixtureSource

__all__ = ["TradeSource", "FixtureSource", "ComtradeSource"]
