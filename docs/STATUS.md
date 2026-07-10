# STATUS — what's happening right now

> Single source of truth for the CURRENT moment. Update at the start and end of every
> session. History goes in `docs/progress/`, not here.

**Last updated:** 2026-07-10 (adopted the file-driven workflow kit; repo bootstrapped)

## Phase
**Stage 0 — validation (NO code).** Plan §12–13: build nothing until the go/kill gate passes.
`main` holds: product plan + this workflow scaffolding. No app code exists yet.

## Active task
**Stage 0 — ADR-0001 — batch 0.1 NOT STARTED (branch `docs/adopt-workflow-kit` merged pending approval).**
Workflow kit adapted to TradePulse: `CLAUDE.md` + `docs/` living docs created on branch
`docs/adopt-workflow-kit`. Awaiting owner approval to merge to `main`.
**NEXT: batch 0.1** — produce the one manual "Wood Pellet Export Opportunities" report
(Vietnamese PDF), per ADR-0001 (branch `phase/0-manual-report` from main).

## Next action (whoever picks this up)
- Owner: review branch `docs/adopt-workflow-kit`; approve merge (see §"How to develop", CLAUDE.md).
- Then start ADR-0001 batch 0.1: hand-build the validation report. No code.
- Confirm/decide the Golden Rule wording (currently "Inform, never match" — CLAUDE.md).

## Watch / before launch
- **Gate:** no MVP code until Stage 0 GO (≥5 substantive replies AND ≥3 willing to pay). Plan §12.
- Pilot-vertical fallback undecided if pellet exporters don't respond (tea/seafood/cashew) — plan §15 Q1.
- Price point (200k vs 500k VND) tested in Stage 0 conversations — plan §15 Q2.
- Comtrade rate limits: cache raw pulls aggressively when Phase 1 starts.
