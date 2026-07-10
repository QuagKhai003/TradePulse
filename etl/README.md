# etl — TradePulse data pipeline (Layer 1)

Python 3.11+ (tested on 3.14). **Stdlib only — no `pip install` needed.**

## Run
```bash
cd etl
python -m tradepulse_etl                 # load trade_flows from the offline sample (default)
python -m tradepulse_etl --source comtrade --period 2025   # live UN Comtrade (rate-limited)
python -m unittest discover -s tests     # deterministic offline tests
```
Builds/updates `../data/tradepulse.sqlite` (gitignored — derived, re-buildable).

## Layout
```
tradepulse_etl/
  config.py        # pilot scope: HS pellets, markets, signal thresholds (plan §3, §6)
  db.py            # SQLite schema + upserts (persistence seam -> Postgres later)
  transform.py     # raw record -> trade_flows row (PURE)
  signals.py       # trade_flows -> signals (PURE, deterministic)   [batch 1.2]
  pipeline.py      # pull -> store raw -> transform -> upsert
  sources/         # the data-source seam: base + fixture (offline) + comtrade (live)
data/fixtures/     # bundled SAMPLE raw data (not real figures) + its generator
tests/             # offline unit tests
```

## Principles (plan §6, §10.4)
- **Raw-before-transform:** every pull is written to `../data/raw/<source>.json` before transform.
- **Deterministic:** transform + signals are pure functions; no clock/network in the logic path.
- **Importer-reported** import flow is the default consistent side (plan §6.4).
- Sample data is labelled everywhere — never mistaken for published statistics.
