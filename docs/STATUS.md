# STATUS — what's happening right now

> Single source of truth for the CURRENT moment. Update at the start and end of every
> session. History goes in `docs/progress/`, not here.

**Last updated:** 2026-07-10 (batch 1.1 ETL done + merged; building skeleton toward localhost MVP)

## Phase
**Phase 1 MVP — sequential build (owner direction).** Stage 0 validation deferred (ADR-0001 on
record). Goal this stretch: a Next.js app runnable on `localhost` showing pellet demand signals.

## Active task
**Phase 1 — ADR-0002 — batch 1.1 DONE (merged to `main`).** Python ETL (`etl/`, stdlib-only)
pulls pellet HS × 5 markets behind a source seam (fixture offline / Comtrade live), stores raw,
upserts `trade_flows` in `data/tradepulse.sqlite`. `python -m tradepulse_etl` = 42 rows; 2 tests green.
**NEXT: batch 1.2** — signal compute (branch `phase/1-signals`): pure YoY bands over `trade_flows`
→ `signals` + export a `web/` JSON snapshot; deterministic offline test on every band + noise floor.

## Next action (whoever picks this up)
- Batch 1.2 signals (+test + web snapshot), then 1.3 Next.js map → first localhost render.
- Run so far: `cd etl && python -m tradepulse_etl` then `python -m unittest discover -s tests`.
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
