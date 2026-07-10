# STATUS — what's happening right now

> Single source of truth for the CURRENT moment. Update at the start and end of every
> session. History goes in `docs/progress/`, not here.

**Last updated:** 2026-07-10 (ADR-0002 Phase 1 plan written; two parallel branches open, unmerged)

## Phase
**Stage 0 — validation (NO code per plan).** Plan §12–13: build nothing until the go/kill
gate passes. `main` holds product plan + the file-driven workflow docs. No app code yet.

## Active task
**Parallel tracks decided (owner): validate + build skeleton at once.** Two branches open off
`main`, both committed, **awaiting owner approval to merge:**
- `docs/adr-0002-phase1-plan` — ADR-0002 (Phase 1 MVP batch plan 1.1–1.9) written + accepted.
- `phase/0-manual-report` — Stage 0 batch 0.1: Vietnamese validation report scaffold.
**NEXT after approvals:** batch 1.1 (branch `phase/1-etl-comtrade`) — Python ETL Comtrade →
`trade_flows`; start filling the Stage 0 report with real sourced data.

## Next action (whoever picks this up)
- **Owner: review + approve the two open branches to merge** (see CLAUDE.md working agreement).
- Then batch 1.1 ETL (walking-skeleton step 1 of 3). Then 1.2 signals, 1.3 map.
- Fill the Stage 0 report (batch 0.1) with real sourced figures, then distribute (0.2).
- Confirm Golden Rule wording ("Inform, never match" — CLAUDE.md).
- Decide pilot-vertical fallback if pellet exporters go silent (tea/seafood/cashew — plan §15 Q1).

## Path to MVP (Phase 1 — see docs/ROADMAP.md, gated on Stage 0 GO)
Dependency order: 1.1 ETL(Comtrade→trade_flows) → 1.2 signal compute(+test) → 1.3 map+feed →
1.4 category search → 1.5 country drill-down → 1.6 profiles → 1.7 requirement pages →
1.8 watch/alerts+telemetry → 1.9 payments. Firm up in ADR-0002 before coding.

## Watch / before launch
- **Gate:** no MVP code until Stage 0 GO (≥5 substantive replies AND ≥3 willing to pay). Plan §12.
- Pilot-vertical fallback undecided if pellet exporters don't respond (tea/seafood/cashew) — plan §15 Q1.
- Price point (200k vs 500k VND) tested in Stage 0 conversations — plan §15 Q2.
- Comtrade rate limits: cache raw pulls aggressively when Phase 1 starts.
