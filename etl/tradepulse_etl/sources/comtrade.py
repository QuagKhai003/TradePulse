"""
comtrade.py — live UN Comtrade source (the production impl of the seam).
@context  Real trade flows from the free Comtrade API (plan §9.1). Optional for the MVP, which
          ships on the fixture; wired so switching to real data is one CLI flag, no caller change.
@done     Builds the v1 preview request per reporter, fetches via stdlib urllib (no pip dep),
          normalises to the same raw shape fixture.py returns (Comtrade-shaped dicts).
@todo     Add API-key auth + monthly->quarterly aggregation + retry/backoff when we go live.
@limits   Network I/O. Rate-limited (plan §14) — cache raw pulls; do not call in the fast test loop.
@affects  Implements base.TradeSource; selected by pipeline when --source=comtrade.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

# Free preview endpoint (no key, strict rate limits). period=quarterly not offered directly;
# production will pull monthly and aggregate. Kept minimal + documented for the swap.
BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"


class ComtradeSource:
    name = "comtrade"

    def __init__(self, period: str, timeout: int = 30):
        self.period = period  # e.g. "2025" (annual preview); real impl will do quarters
        self.timeout = timeout

    def pull(self, hs_codes: list[str], reporters: list[int], partners: list[int] | None) -> list[dict]:
        out: list[dict] = []
        for reporter in reporters:
            params = {
                "reporterCode": reporter,
                "period": self.period,
                "cmdCode": ",".join(hs_codes),
                "flowCode": "M",
            }
            if partners:                    # None -> let Comtrade return all partners
                params["partnerCode"] = ",".join(str(p) for p in partners)
            url = f"{BASE}?{urllib.parse.urlencode(params)}"
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            out.extend(self._normalise(payload.get("data", [])))
        return out

    @staticmethod
    def _normalise(rows: list[dict]) -> list[dict]:
        # Map Comtrade fields to the raw shape the transform expects. period YYYY -> 'YYYY-Q?'
        # is deferred to the aggregation step; kept explicit so the seam stays honest.
        return [
            {
                "reporterCode": r.get("reporterCode"),
                "partnerCode": r.get("partnerCode"),
                "cmdCode": str(r.get("cmdCode")),
                "period": str(r.get("period")),
                "flowCode": r.get("flowCode", "M"),
                "primaryValue": r.get("primaryValue"),
                "netWgt": r.get("netWgt"),
                "qtyUnitAbbr": r.get("qtyUnitAbbr", "kg"),
                "publishedDate": r.get("publicationDate"),
            }
            for r in rows
        ]
