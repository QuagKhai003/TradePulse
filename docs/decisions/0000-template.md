# ADR-NNNN — <title>

**Status:** Proposed | Accepted | Accepted — COMPLETE | Superseded by ADR-XXXX · <date>
· Builds on <ADR refs>.

## Context
<The problem / forces. Why we need a decision now. What's broken or missing.>

## Decision & key rules (apply to every batch)
- <The decision, stated plainly.>
- <Rule/constraint that holds across all batches — e.g. "deterministic signals", "cite every
  source", "inform never match", "behind a seam".>

## Plan (batches — branch per batch, tested, docs each batch)
> The first unchecked box is "what's next." Tick `[ ]` → `[x]` with a one-line result when a
> batch merges (after owner approval).

- [ ] **N.1 — <slice>.** <What it delivers + acceptance in a line.>
- [ ] **N.2 — <slice>.** <…>
- [ ] **N.3 — <slice>.** <…>

## Acceptance
- <Observable condition 1 that proves the phase is done.>
- <Condition 2. Tests green; build/lint clean; the Golden Rule held.>

## Notes for the executor
- Sequence is by dependency: N.1 → N.2 → N.3.
- Conventions: see `docs/CONVENTIONS.md`. Update STATUS + progress (+ DATA_MODEL) each batch.
- Git: branch per batch from `main`; conventional commits; **no merge without owner approval**;
  no push without approval; no AI attribution in commits.
