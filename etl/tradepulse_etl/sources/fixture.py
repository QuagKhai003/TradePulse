"""
fixture.py — offline sample source (the local impl of the seam).
@context  Lets the whole pipeline + web run with zero network/API key. SAMPLE data, not real
          figures — clearly labelled everywhere so no one mistakes it for published trade stats.
@done     Loads etl/data/fixtures/pellets.json; filters to requested HS/reporters/partners.
@todo     Nothing — swap to ComtradeSource for real numbers.
@limits   Reads one bundled JSON file. Deterministic. No network.
@affects  Implements base.TradeSource; used by pipeline when --source=fixture (default).
"""
from __future__ import annotations

import json
from pathlib import Path

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "pellets.json"


class FixtureSource:
    name = "fixture"

    def __init__(self, path: Path | str = FIXTURE_PATH):
        self.path = Path(path)

    def pull(self, hs_codes: list[str], reporters: list[int], partners: list[int]) -> list[dict]:
        records = json.loads(self.path.read_text(encoding="utf-8"))
        hs, rep, par = set(hs_codes), set(reporters), set(partners)
        return [
            r for r in records
            if r["cmdCode"] in hs and r["reporterCode"] in rep and r["partnerCode"] in par
        ]
