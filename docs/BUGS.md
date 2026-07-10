# BUGS & LIMITATIONS

> Log it the moment you hit it. Don't wait, don't rely on memory. Each entry: an id, the
> symptom, the cause if known, status, and where it's handled.

Format: `L-NNN` (limitation) / `B-NNN` (bug) / `S-NNN` (security/launch risk).

---

## L-001 — Trade data lags 1–6 months
- **Symptom:** figures shown are never real-time; Comtrade lags 1–6 mo, national sources 1–2 mo.
- **Cause:** inherent to free/official trade statistics + revisions.
- **Status:** addressed-by-design (dormant until Phase 1).
- **Where:** plan §6.4; every figure must carry a publication-period + date label. `signals`/UI.
- **Notes:** re-pull trailing 4 quarters on every refresh (revisions). Never imply real-time.

## L-002 — Mirror discrepancies (exporter vs importer reported)
- **Symptom:** exporter-reported and importer-reported values differ (freight, misclassification).
- **Cause:** two independent customs systems report the same flow.
- **Status:** addressed-by-design.
- **Where:** plan §6.4. Default importer-reported per view; state it in a tooltip.
- **Notes:** Vietnam-tile headline side (GDVC vs importer) still open — plan §15 Q4.

## L-003 — Comtrade free preview: annual World-only (no quarterly, no partners)
- **Symptom:** live `--source comtrade` returns ANNUAL World totals only; drill-down shows "no
  sourcing data"; signals are annual YoY, not quarterly.
- **Cause:** the keyless preview endpoint rejects multi-period requests (HTTP 400) and rate-limits
  bursts (HTTP 429), so monthly→quarter aggregation across markets × partners is infeasible without
  a subscription key. Also returns the World total split by transport-mode/2nd-partner — only the
  canonical `motCode=0, partner2Code=0` row is the true total (double-count bug, now filtered + tested).
- **Status:** RESOLVED (2026-07-11) with a free key. `comtrade.py` DUAL-MODE: `etl/.env` key →
  authenticated monthly `/data` (periods chunked ≤12/call — the endpoint caps at 12) → quarter
  aggregation + all-partner breakdown = full design. Verified live: flows=346, latest 2026-Q1,
  quarterly signals + partner sourcing charts. No key → keyless annual World-only fallback.
- **Where:** `etl/tradepulse_etl/sources/comtrade.py`, `settings.py` (.env loader).
- **Notes:** free key at https://comtradedeveloper.un.org/ (`etl/.env.example`). No paid tier / scraping.

## S-001 — Accuracy liability (outdated requirement → rejected container)
- **Symptom:** a stale Layer-3 requirement could cause a user's shipment to be rejected at port.
- **Cause:** Layer 3 is a curation business; sources change.
- **Status:** open — mitigations mandated before any Layer-3 ships.
- **Where:** plan §14, §8. Source link + verified date per item; "last full review" per page;
  change log; "official sources govern" disclaimer.
- **Notes:** hard cap ≤20 requirement pages until revenue (maintenance burden, plan §14).
