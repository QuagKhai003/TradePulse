# ADR-0001 — Stage 0: manual report validation before any code

**Status:** Accepted — IN PROGRESS · 2026-07-10 · Builds on: product plan §12–13.

## Context
The generic "global demand + buyer directory" product already exists free (ITC/Trade Map) and
at scale (Volza, Panjiva, Tridge). Our bet is a narrow wedge: plain-language signals +
per-market qualification requirements + change alerts, Vietnamese-first, for SME factory owners.
That bet is unproven. The single largest risk (plan §14) is **willingness-to-pay** — SMEs read
free and may not pay. Building an MVP before testing this burns 6–8 weeks against an unknown.

Plan §12 is explicit: **build nothing until Stage 0 passes.** Validate with one hand-made
report, not code.

## Decision & key rules (apply to every batch)
- **No code ships in Stage 0.** Output is a PDF + outreach + a measured decision. Any engineering
  temptation is deferred to Phase 1 (ADR-0002), which is gated on a GO here.
- **Inform, never match** (Golden Rule) — the report informs; it never introduces parties.
- **Cite every claim.** Requirement checklist items and signals in the report carry official
  sources + dates, exactly as the product would (dogfoods plan §8).
- **Deterministic signals.** The top-5 destination signals are computed by hand from published
  stats with the plan §6 formula — no guessing.
- Record the outreach + responses as durable evidence (spreadsheet/notes committed or linked),
  so the GO/PIVOT/KILL call is defensible and resumable.

## Plan (batches — branch per batch, docs each batch)
> First unchecked box = "what's next." Tick `[ ]` → `[x]` with a one-line result when done
> (after owner approval).

- [ ] **0.1 — Build the validation report.** "Wood Pellet Export Opportunities — [month]",
  Vietnamese PDF: active Korean/Japanese tenders; policy changes (Japan FIT/SBP, Korea subsidy
  direction); reference prices; top-5 destination signals computed by hand (plan §6); 10
  certified foreign buyer profiles from FSC/SBP DBs; 1-page "pellets → Japan" requirements
  checklist. **Done when:** PDF exists, every figure/requirement sourced + dated.
- [ ] **0.2 — Distribute to 20–30 exporters.** VIFOREST members, wood-industry Facebook/Zalo
  groups, direct email to company-site contacts. **Done when:** ≥20 recipients logged (list
  committed/linked, no private contact data in git).
- [ ] **0.3 — Measure + decide.** Track replies, follow-up questions, and the one that matters:
  "would you pay [200k–500k VND]/month for this arriving automatically?" Record GO/PIVOT/KILL.
  **Done when:** decision written into STATUS + progress with the evidence.

## Acceptance
- The report was sent to ≥20 real exporters and responses are recorded.
- A GO/PIVOT/KILL decision is documented against the gate below.
- **Gate (plan §12):** GO = ≥5 substantive replies AND ≥3 say yes to paying anything →
  write ADR-0002 (Phase 1 MVP). PIVOT = strong engagement, zero willingness-to-pay → repeat
  Stage 0 on another vertical (tea/seafood/cashew). KILL = <3 replies across two verticals → stop.

## Notes for the executor
- Sequence: 0.1 → 0.2 → 0.3.
- This phase is mostly non-engineering; still follow the workflow — branch per batch, update
  STATUS + progress, tick boxes. Log all progress (plan §"record everything").
- Keep private contact lists OUT of git (gitignored `data/` or external sheet); commit only
  aggregate/anonymized outreach counts + outcomes.
- Git: branch per batch from `main`; **no merge without owner approval**; no push without approval.
