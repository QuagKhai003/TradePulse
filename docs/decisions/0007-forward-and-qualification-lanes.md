# ADR-0007 — Forward-demand + qualification-change lanes (separate display, never merged)

- **Status:** Accepted — 2026-07-15 (owner approved). Adds two NEW data types beside the customs flow lane.
- **Context:** All the trade-flow sources we use (Comtrade, BACI, national customs, mirror) are the SAME
  underlying customs data reshuffled — backward-looking, and merged one-number-per-cell. The owner asked
  for genuinely *different* data that enriches the app beyond "live signal + buyers/sellers/past-orders".
  Two non-customs data types fit the product and the Golden Rule:
  - **USDA PSD** — global commodity balance sheets + **forward trade FORECASTS** (production, supply,
    exports/imports, per country, per marketing year). Forward-looking where customs stats lag.
  - **Regulatory-change feeds** (WTO ePing SPS/TBT notifications; likely EU RASFF border rejections) —
    *events*, not numbers: a market changing an import rule, or rejecting a shipment.

## The decision (and the guarantee it protects)
These are **separate lanes**, each keyed on `(hs6, market)` like everything else, but they **never merge
into the customs number**. The one-number-per-cell merge (`merge.merge_flows`) stays *inside* the flow
lane only. Three lanes converge at the product×market view; each renders as its own source-labeled row/
line:

| Lane | Data type | Table | Renders as | Answers |
|---|---|---|---|---|
| **Flow** (existing) | customs value/qty | `trade_flows` | map colour + history chart | what IS / was |
| **Forward** (new) | USDA PSD forecast | `forecasts` | dashed forward line on the same chart, labeled "USDA forecast" | what's COMING |
| **Events** (new) | regulatory change | `regulatory_events` | qualification tab (Layer-3) items + change-alerts | what CHANGED |

**Why never merge:** a forecast is not a customs measurement, and a rule-change is not a number. Summing
or averaging them into the displayed flow would (a) break **deterministic signals** (the map number must
stay a reproducible formula over published *customs* data — plan §6) and (b) put an unlabeled non-customs
figure on screen. So they sit *beside* the number, each with its own source link + date, never fused.

## Golden-Rule + determinism compliance
- **Forward lane:** PSD is official, public, deterministic. The forecast line is drawn from PSD's own
  published numbers, labeled as a forecast with its source + marketing year — never blended with the
  customs series, never presented as an actual.
- **Events lane:** WTO/RASFF expose public regulatory acts + official source URLs — exactly Layer-3
  material (each requirement item already must cite a source + verified date). No private party, no
  matching. A RASFF rejection names the *notifying country + product + reason + notice URL*, not a
  brokered contact.

## Coverage is honest and uneven (state it in the UI)
- **PSD covers major agricultural commodities only** (grains, oilseeds, coffee, cotton, meat, sugar,
  cotton…). Great for our tea/coffee/shrimp*/cashew/rice; **useless for wood pellets / sawn wood.** It is
  a *targeted* forward overlay, not universal — products it doesn't cover simply show no forecast line.
  (*seafood is PSD-partial; verify per product.) PSD "commodity" ≠ HS, so a `commodity → hs6` map is
  needed (same pattern as `cpv_by_hs.json` for tenders).
- **Regulatory feeds are broad** (any product) but classification to HS is keyword/scope-matched — same
  honesty caveat as TED baskets; low-confidence matches are dropped, not shown as fact.

## Consequences
- Two new tables (`forecasts`, `regulatory_events`) + two new export files (`forecast-<hs>.json`,
  `events-<hs>.json`), joined on `(hs6, market)` which the map/country page already resolve — no
  re-architecture of the flow pipeline.
- Two new ETL sources (`sources/psd.py`, `sources/eping.py` and/or `sources/rasff.py`), pulled by the
  periodic batch (monthly cadence — these are not per-open lazy builds).
- **PSD needs a free FAS key** (`apps.fas.usda.gov/opendataweb`, separate from api.data.gov) →
  `etl/.env` as `FAS_PSD_KEY`. Regulatory feeds are keyless.
- The app gains two dimensions — *forward forecast* and *live requirement changes* — on top of live
  signal + buyers/sellers/past-orders, without touching the deterministic customs number.
