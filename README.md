# TradePulse — Export Intelligence Terminal

> **A map-first web app that tells a Vietnamese factory owner where global demand for their product is moving, who the public buyers are, and exactly what it takes to qualify for each destination market — in plain language, every claim sourced.**

TradePulse is an *information terminal, not a marketplace*. It informs; the user acts. It never introduces a buyer to a seller, never brokers a contact, never touches a transaction. That single constraint is what makes the data trustworthy and the product cheap to run.

---

## The problem it solves

A wood-pellet mill in Bình Dương knows how to *make* the product. What it can't see is the market: Is Japanese demand rising or falling this quarter? Which countries are buying more? What certification does Korea now require at the border — and did that rule just change?

That intelligence exists, but it's locked inside analyst tools (Volza, Panjiva, Tridge, ITC Trade Map) that **sell databases to analysts**. A factory owner doesn't want a database — they want *answers*.

**The wedge:** TradePulse sells answers to factory owners. Plain-language signal cards, per-market qualification checklists, and change alerts — Vietnamese-first.

---

## What it does

Everything is organized in three layers, drilling from *"where is demand?"* down to *"what do I need to ship there?"*.

### Layer 1 — Where demand is moving
- **World choropleth map** (up to ~177 countries), colored by a deterministic demand signal, toggled between **export** and **import** flows.
- **Per-product maps** for **1,240 products** — every HS4 heading plus curated HS6 pilot products. Search by name *or* HS code and the map swaps to real per-product data.
- **Country drill-down**: export & import value, year-over-year band, historical trend, and **partner sourcing tables for all 226 reporter countries** (who each country sells to / buys from). The five focus markets (VN, JP, KR, US, UK) additionally get **quarterly-resolution** partner charts.

### Layer 2 — Who the public buyers are
- A **market feed** of *public* buyers, sellers, and past orders for the country you're viewing — sourced from government procurement systems, showing **organisation names + the official record link only**.
- Coverage spans nine national procurement systems: EU, US, UK, Korea, Ukraine, Moldova, Australia, Chile, Dominican Republic.

### Layer 3 — What it takes to qualify
- **Per-market qualification requirements** for a product×market pair — the certifications, documents, and standards you need to clear the border.
- **Every requirement cites an official source link + a "last verified" date.** No source = it does not ship. A wrong requirement can reject a container, so this bar is absolute.
- **Regulatory change watch**: upcoming import-rule changes (WTO ePing SPS/TBT notifications), each with its comment deadline and source.

### Cross-cutting
- **Forward outlook lane** — USDA PSD supply/demand *forecast* (quantities), kept visually distinct from customs figures so it never reads as a trade number.
- **World price lane** — IMF PCPS commodity price trend, shown beside the flow chart as a direction cue.
- **Watch & alerts** — follow a signal or a market and get notified on change.
- **Bilingual** — Vietnamese-first, English via `?lang=en`.

---

## Live walkthrough

Run it locally (one command, below), then:

| Step | URL | What you see |
|---|---|---|
| Landing | `http://localhost:3200` | World map colored by wood-pellet demand signal; global feed of movers |
| Search a product | type `coffee` or `0901` | Map swaps to real per-product trade data |
| Drill a country | click a country → `/country/392?hs=0901` | Japan's coffee: value, YoY, partner sourcing, price + outlook lanes |
| Public buyers | US crude oil → `/country/842?hs=2709` | US Dept of Energy / Strategic Petroleum Reserve contracts under *Past orders* |
| Qualification | wood pellet → Japan | Certifications + documents to clear the border, each source-linked |

Honest empty states are a feature: a product with no public buyers, no curated requirement page, and no regulatory notice shows **"No available data yet"** rather than an invented answer.

---

## Data — real and cited

Nothing here is mocked. Every number is a reproducible formula over published data; **an LLM never produces a figure the app displays.**

| Domain | Source |
|---|---|
| Trade flows (signals) | UN Comtrade (authenticated: quarterly + partners) · CEPII **BACI** (annual bilateral, all countries) |
| Public buyers / past orders | EU **TED** · US **USAspending** · UK **OCDS** (Contracts Finder, Find-a-Tender, Scotland) · Korea **KONEPS** · Ukraine **ProZorro** · Moldova **MTender** · Australia **AusTender** · Chile **ChileCompra** · Dominican **DGCP** |
| Public sellers | EU **DG SANTE** approval registries |
| Forward outlook | USDA **PSD** supply/demand forecast |
| World price | IMF **PCPS** |
| Regulatory changes | WTO **ePing** (SPS/TBT) · EU **RASFF** |

---

## Tech stack

Deliberately boring and cheap — monthly/quarterly batch data, no streaming, no per-request billing.

- **ETL / pipeline** — Python (standard library only), cron-scheduled batch → SQLite star schema over trade flows.
- **Frontend** — Next.js 15 (App Router, SSR for SEO on public map/category pages).
- **Map** — D3 / MapLibre choropleth over free GeoJSON. No Google Maps billing.
- **Layer-3 CMS** — Markdown in-repo, so git history *is* the change log and audit trail.
- **Web/ETL seam** — the ETL writes slim per-product JSON snapshots; the web app reads them at request time (with an in-process mtime cache), so re-running the pipeline shows up without a rebuild.

---

## Getting started

**One command** (fetches real trade data on first run if the snapshot is missing):

```bash
cd web && npm install && npm run dev     # → http://localhost:3200   (add ?lang=en for English)
```

`npm run dev` auto-runs the ETL first (`predev` → `scripts/prepare-data.mjs`): it fetches real UN Comtrade data if the snapshot is missing, refreshes in the background if it's stale (>24h), or skips if fresh. Force a refresh with `npm run data`.

**Optional API keys** unlock fresher/deeper data — all free, all in `etl/.env` (gitignored; see `etl/.env.example`):

- `COMTRADE_SUBSCRIPTION_KEY` — quarterly + partner breakdown (keyless falls back to annual, World-only).
- `USDA_API_KEY` — USDA PSD forward outlook.
- `KCS_SERVICE_KEY`, `CENSUS_API_KEY`, `ESTAT_APP_ID` — Korea / US Census / Eurostat national feeds.

**Run the tests** (offline, deterministic — signal math, alerts, source helpers):

```bash
cd etl && python -m unittest discover -s tests      # 21 test modules
```

---

## Project structure

```
docs/            Living documentation — read these first (ONBOARDING, CONVENTIONS, ROADMAP, STATUS, ADRs)
etl/             Python data pipeline (Layer-1 flows, Layer-2 buyers, Layer-3 events) + tests
  tradepulse_etl/
    sources/     One module per data source (comtrade, baci, ted, usaspending, ocds, koneps, …)
    reference/   HS↔CPV crosswalk, UNSPSC map, product catalog, country codes
web/             Next.js frontend + API (App Router)
  app/           Pages (map, country drill, requirements, profiles, pricing) + components + lib loaders
  public/data/   ETL-generated per-product JSON snapshots (the web/ETL seam)
content/         Layer-3 qualification pages + company profiles (markdown/JSON, one concept per file)
trade-signal-terminal-plan.md   Full product vision (source of truth for scope)
```

---

## Design principles (non-negotiable)

1. **Inform, never match.** The app never introduces two parties. Layer 2 shows public names + source links only — never private/verified contact data. If a feature introduces a buyer to a seller, it stops.
2. **Deterministic signals only.** Every signal is a reproducible formula over published data. No AI-guessed trends, ever.
3. **Every requirement cites its source.** Each Layer-3 item shows an official source link + a "last verified" date, or it doesn't ship.

---

## Status

**Phase 1 MVP — complete and running on `localhost:3200`.** Map + signals + search + country drill-down + Layer-2 public-buyer profiles + Layer-3 requirement pages + watch/alerts. Data is real across all three layers. Willingness-to-pay (Stage 0) is not yet validated — this is a working product prototype, not a launched business.

See [`docs/STATUS.md`](docs/STATUS.md) for live detail and [`docs/ROADMAP.md`](docs/ROADMAP.md) for phase scope.

## About

See [`ABOUT.md`](ABOUT.md) for the story behind the project — the insight, the positioning, and why "inform, never match" is the whole thing.
