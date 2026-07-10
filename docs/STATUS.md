# STATUS — what's happening right now

> Single source of truth for the CURRENT moment. Update at the start and end of every
> session. History goes in `docs/progress/`, not here.

**Last updated:** 2026-07-10 (batch 1.2 signals + snapshot done + merged; next = 1.3 Next.js map)

## Phase
**Phase 1 MVP — sequential build (owner direction).** Stage 0 validation deferred (ADR-0001 on
record). Goal this stretch: a Next.js app runnable on `localhost` showing pellet demand signals.

## Active task
**Phase 1 — ADR-0002 — batches 1.1 + 1.2 DONE (merged to `main`).** ETL loads `trade_flows`,
`signals.compute_signals` (PURE) fills `signals`, `export.py` writes `web/public/data/snapshot.json`.
`python -m tradepulse_etl` → flows=42, signals=8, feed=4. 8 offline tests green.
**NEXT: batch 1.3** — Next.js app (branch `phase/1-map`): D3/SVG choropleth + signal feed reading
the snapshot; export/import toggle, honest period + SAMPLE labels, VN default. First localhost render.

## Next action (whoever picks this up)
- Batch 1.3: scaffold `web/` (Next.js), render map + feed from `snapshot.json` → `npm run dev` on localhost.
- Rebuild data anytime: `cd etl && python -m tradepulse_etl` (regenerates the snapshot).
- Confirm Golden Rule wording ("Inform, never match" — CLAUDE.md).
- Decide pilot-vertical fallback if pellets stall (tea/seafood/cashew — plan §15 Q1).

## Path to MVP (localhost) — see docs/ROADMAP.md
Skeleton: **1.1 ETL ✅ → 1.2 signals(+test) → 1.3 map+feed** = runnable localhost demo.
Then 1.4 search → 1.5 drill-down → 1.6 profiles → 1.7 requirement pages → 1.8 alerts → 1.9 payments.

## Watch / before launch
- **Data is SAMPLE (fixture), clearly labelled.** Swap to real Comtrade (`--source comtrade`) +
  monthly→quarter aggregation before any external launch. Never imply the sample is published stats.
- Stage 0 willingness-to-pay still unproven — plan §12 gate deferred, not cleared.
- Price point (200k vs 500k VND) — plan §15 Q2. Comtrade rate limits: cache raw pulls.
