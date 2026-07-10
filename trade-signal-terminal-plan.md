# TradePulse — Export Intelligence Terminal
## Product Plan v1.0

> **Working name:** "TradePulse" is a placeholder — rename freely.
> **One-liner:** A map-first web app that shows Vietnamese SME exporters where global demand for their product is moving, who the buyers and sellers are, and exactly what it takes to qualify for each destination market — information only, no matchmaking.

---

## 1. What this is (and is not)

| This IS | This is NOT |
|---|---|
| An **information terminal** — the app informs, the user acts | A marketplace or matching platform |
| A **signal radar** — surfacing demand/supply changes worth attention | A raw customs-records database (that's Volza/Panjiva's game) |
| A **qualification guide** — per product × destination market | A broker, agent, or party to any transaction |
| A **watchdog** — alerts when something the user cares about changes | A one-time encyclopedia people read once and cancel |

**Core positioning decision (locked):** Everything is independent. The app never matches a buyer to a seller, never introduces parties, never touches a transaction. This removes the trust/verification/liability problem that forced Tridge to raise $121M and hire 500+ field agents.

---

## 2. Market reality (why the obvious version loses)

The generic "see global demand + buyer/supplier directory" product already exists at three price points:

| Competitor | What it does | Price |
|---|---|---|
| **ITC Export Potential Map / Trade Map** (UN/WTO agency) | Country-level untapped export potential, bilateral trade flows, 226 countries × 4,000+ products | **Free** |
| **Volza** | 3B+ shipment records, 209 countries, verified buyer/supplier contacts, alerts | ~$1,500/yr |
| **Panjiva (S&P), ImportGenius, Tendata** | Premium shipment-level trade intelligence | $15k–50k+/yr |
| **Tridge** | Agri-food buyer↔supplier matching + verification + fulfillment | Commission model, $2.7B valuation |

**Conclusion:** We cannot win on data breadth (free tools + billion-record incumbents squeeze the price to zero). We win on a slice they all ignore.

### The wedge
Incumbents sell **databases to analysts**. We sell **answers to factory owners**:
1. Free/lagging macro data → translated into plain-language signal cards ("Japan pellet demand ▲ significant, driven by FIT subsidy — here's why and what to do").
2. **Per-market qualification requirements** — fragmented across regulators, certifiers, and tender docs; nobody packages them for Vietnamese SMEs in Vietnamese.
3. **Change alerts** — the recurring-revenue engine. Static info is read once; alerts are rented monthly.

---

## 3. Target user & scope (locked)

- **User:** Vietnamese SME exporter / aspiring exporter. Not an analyst. May not know their own HS code. Reads Vietnamese first, English second.
- **Geographic scope:** Vietnam-out only (Vietnam as the exporting country of interest).
- **Vertical scope for v1:** 2–3 product verticals maximum.
  - **Pilot vertical:** Wood pellets & wood products (HS 4401.31 and neighbors). Rationale: >$1B Vietnamese export, ~500 exporters, demand driven by *trackable* signals (Japan FIT/FIP policy, Korean utility tenders, FSC/SBP certification gates), buyers concentrated and identifiable.
  - Candidate second verticals: tea/coffee, seafood, cashew — decide via Stage 0 feedback + locked-page telemetry (§7.6).
- **Destination markets for depth layers:** 5–8 (pilot: Japan, South Korea, EU, US, UK).
- **The global map exception:** Layer 1 (map + flows) covers *all* countries and products because the underlying data is free and uniform. Depth (Layers 2–3) exists only for covered verticals; everything else is a locked page.

---

## 4. Product principles (non-negotiable rules)

1. **Inform, never match.** No introductions, no contact brokering, no deal participation.
2. **Values, not order counts.** Free data provides trade *value* (USD) and *volume* (tons); transaction/shipment counts require paid customs data. All UI displays value/volume + change %. Never fabricate "number of orders."
3. **Deterministic signals only.** Every signal is a reproducible formula over published data (§6). No AI-guessed trends.
4. **Every requirement cites its source.** Each qualification item shows the official source link + "last verified" date. No source = do not publish. A wrong requirement can cost a user a rejected container.
5. **Honest timestamps.** Trade data lags 1–3 months. Every period is labeled ("Q1 2026 · published May 2026"). Never imply real-time.
6. **HS codes are never an input.** Users search in everyday Vietnamese/English words; the app maps to HS behind the scenes and displays the code as an educational badge (§7.2).
7. **Locked pages are telemetry.** Uncovered verticals/markets show "coming soon — request it"; every click is logged as demand evidence for what to build next.
8. **Qualification pages exist only at product × market granularity.** Never country-level alone.

---

## 5. Product architecture — three layers + the alert engine

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1 · Demand/supply map & flows      [FREE HOOK] │
│ Global, all products. UN Comtrade + national stats.  │
│ Value: gets users in the door. Moat: none.           │
├─────────────────────────────────────────────────────┤
│ LAYER 2 · Buyer/seller directory        [MID VALUE]  │
│ Names + public profiles + source links. No matching. │
│ Covered verticals only. Moat: hand curation.         │
├─────────────────────────────────────────────────────┤
│ LAYER 3 · Market entry requirements     [PAID CORE]  │
│ Per product × destination. Source + verified date.   │
│ Moat: maintained accuracy (a curation business).     │
├─────────────────────────────────────────────────────┤
│ ALERT ENGINE · "Watch this"        [RECURRING REV]   │
│ Signal threshold crossed / new tender / rule changed │
│ Push, not pull. This is what renews subscriptions.   │
└─────────────────────────────────────────────────────┘
```

**Key insight driving this design:** everything in Layers 1–3 is *pull* (look-up content, value extracted in month one → churn). The alert engine is *push* — the app watches while the user runs their factory. The screens are the showroom; the watch button is the product being rented.

---

## 6. Signal logic (deterministic spec)

### 6.1 Base computation
- **Granularity:** reporter country × HS-6 product × quarter, split by flow (export / import).
- **Comparison:** year-over-year (same quarter last year). **Never quarter-over-quarter** — seasonal products (tea, pellets, seafood) make QoQ meaningless.
- **Metric:** `delta = (value_this_period − value_same_period_last_year) / value_same_period_last_year`

### 6.2 Noise floors (all must pass before a signal exists)
| Rule | Threshold (initial; tune later) |
|---|---|
| Minimum trade value this period | ≥ US$10M per quarter for the country×product cell |
| Minimum base (same period last year) | ≥ US$2M (kills divide-by-tiny-number explosions) |
| Minimum history | ≥ 4 quarters of data for the cell |

### 6.3 Signal bands
| Band | YoY change | Display |
|---|---|---|
| (suppressed) | −15% … +15% | not shown — "minor" excluded by design |
| Moderate | ±15–30% | ▲ / ▼ moderate |
| Significant | ±30–60% | ▲ / ▼ significant |
| Surge / Collapse | beyond ±60% | ▲▲ surge / ▼▼ collapse |
| New flow | base ≈ 0, now ≥ $5M | ★ new trade lane |

Declines are signals too — a collapsing market (e.g., Korea reducing pellet subsidies) is exactly what an exporter must hear early.

### 6.4 Data caveats handled explicitly
- **Lag:** label every figure with its publication date.
- **Mirror discrepancies:** exporter-reported and importer-reported numbers differ (freight, misclassification). Pick ONE consistent side per view — default to **importer-reported** (customs enforce imports harder, generally more accurate) and say so in a tooltip.
- **Revisions:** national statistics get revised; re-pull the trailing 4 quarters on every refresh.

---

## 7. UX flows (corrected scenario)

### 7.1 Screen 1 — World map (landing)
- Choropleth world map; each country tile: `Exports $X.XB · ▲12% YoY` (toggle export / import / all).
- Side panel: global signal feed (moderate+ only, per §6.3), filterable by flow direction, sorted by band then value.
- Period selector (quarterly), with honest publication labels.
- Clicking anything drills down; no data dead-ends.

### 7.2 Screen 2 — Category view
- Single search box, everyday words, Vietnamese or English: "trà" → autocomplete → **Tea · HS 0902** chip.
- Behind the scenes: lookup table `hs6 → {description_en, description_vi, synonyms[]}`. For v1's 2–3 verticals this is 30–50 hand-mapped codes (~one afternoon). Do NOT build generic product-classification.
- Curated browse tree ("Wood & biomass," "Tea & coffee") = friendly skin over HS chapter groups.
- Map re-renders for the chosen product: exporter view / importer view toggle, same value+YoY tiles.
- HS badge appears on every subsequent screen — quietly teaches users their own code.

### 7.3 Screen 3 — Country drill-down (e.g., Japan)
- Within-country signals: which products are surging in Japan's imports; top partner countries for the selected product with shares and YoY ("Japan pellet imports: Vietnam 55% ▲, Indonesia 30% ▲▲, Canada 8% ▼").
- Historical sourcing chart (country-level partners over time — the "who sourced from where" feature; this is a straight query on free bilateral data).

### 7.4 Screen 4a — Profiles (Layer 2)
- Buyer/seller **names + public profiles + source links**, hand-curated per covered vertical.
- Sources: certification databases (FSC public certificate search, SBP certificate holders, PEFC), tender award records, trade association member lists (e.g., VIFOREST), exhibition exhibitor lists.
- **Decision (locked): names, not contacts.** Verified contact data is Volza's expensive moat; don't promise what can't be maintained. Each profile links to the company's public site/source.

### 7.5 Screen 4b — Qualifications (Layer 3)
- Grayed out until a product is selected; activates per product × destination market.
- Content per §8 template. Sources: regulators (EU Access2Markets, Japan METI/MAFF circulars), certification schemes, tender documents — **never "recent orders"** (transaction data isn't available and isn't the true source of rules anyway).

### 7.6 Locked pages
- Any uncovered product × market shows: "Requirements for [X → Y] — coming soon. Request it." Log every click with user id + pair. This is the roadmap oracle.

### 7.7 Watch & alerts (the paid product)
- "Watch this" button on every product × country pair and every qualification page.
- Alert event types: (a) signal band crossed per §6.3, (b) new tender matching watched HS + market, (c) qualification page updated ("rule changed").
- Delivery: email first; Zalo OA later (Vietnamese users live on Zalo).
- Digest rules: instant for tenders (deadlines!), weekly digest for signals, instant for rule changes.

---

## 8. Layer 3 — Requirement page template (the paid core)

Every qualification page follows this exact structure. **No source link + verified date = the item does not ship.**

```markdown
# [Product] → [Destination market]
HS code(s): ...        Last full review: YYYY-MM-DD

## Snapshot
2–4 sentences, plain language: can a typical Vietnamese SME
realistically enter this market, and what's the hardest gate?

## Requirements checklist
| # | Requirement | Type | Mandatory? | Evidence you need | Source (official link) | Last verified |
|---|---|---|---|---|---|---|
| 1 | FSC or PEFC CoC certificate | Certification | Yes (de facto) | Certificate no. in FSC DB | fsc.org/... | 2026-06-15 |
| 2 | SBP certification | Certification | Phasing in | ... | sbp-cert.org/... | 2026-06-15 |
| 3 | Phytosanitary / fumigation | Regulatory | Yes | ... | maff.go.jp/... | 2026-06-02 |
| ... | | | | | | |

## Typical buyer expectations (non-regulatory)
Payment terms, volume minimums, spec sheets, sample process —
labeled clearly as "market practice," not law.

## How demand works in this market
Who buys (utilities? trading houses?), via what mechanism
(tenders? long-term contracts?), links to live tender portals.

## Price context
Latest published reference price + source + date.

## Change log
YYYY-MM-DD — what changed, source.
```

The change log is what powers "rule changed" alerts — every edit to a page emits an alert to its watchers.

---

## 9. Data source catalog

### 9.1 Trade flows (Layer 1 — free)
| Source | Coverage | Update | Notes |
|---|---|---|---|
| **UN Comtrade API** | All countries, HS-6, annual + monthly | Lag 1–6 months | Free API key; strict rate limits — cache aggressively, batch pulls |
| **Eurostat Comext** | EU imports/exports, CN-8 detail | Monthly, ~2-month lag | Best source for EU demand |
| **Japan customs / e-Stat** | Japan trade, HS-9 | Monthly, ~1-month lag | Fresher than Comtrade for the pilot's #1 market |
| **Korea K-stat / customs** | Korea trade | Monthly | Pilot market #2 |
| **USITC DataWeb** | US imports, HTS-10 | Monthly | Free, excellent |
| **Vietnam Customs (GDVC) / GSO** | Vietnam-reported exports | Monthly summaries | Cross-check mirror data |

### 9.2 Forward demand (alerts)
- **Korean utility pellet tenders** (KOMIPO, KOSPO, KOEN, etc.) — published auctions; the single most valuable scrape in the pilot vertical.
- **EU TED** (Tenders Electronic Daily) — public procurement, free API.
- National eProcurement portals per covered market (add as verticals expand).

### 9.3 Qualification sources (Layer 3)
- **EU Access2Markets** (tariffs + product rules per HS), **CBI** market-entry guides (excellent, free, EU-focused).
- Japan: METI / MAFF circulars; FIT/FIP program documents; SBP rollout notices.
- Certification scheme databases: **FSC certificate search, SBP certificate holders, PEFC** — double duty: requirements evidence (L3) + company directory seed (L2).
- Destination customs/standards agencies per market.

### 9.4 Directory seeds (Layer 2)
Certification DBs above + tender award records (name winning suppliers & buying entities) + association member lists (VIFOREST) + exhibition exhibitor lists.

### 9.5 Prices
Industry association reports (e.g., pellet reference prices per market), published trade statistics unit values (value ÷ volume) as fallback — always labeled with source + date.

---

## 10. Technical requirements

### 10.1 Stack (deliberately boring & cheap)
| Piece | Choice | Why |
|---|---|---|
| ETL / pipeline | **Python** (requests, pandas), cron-scheduled | Simple batch jobs; data updates monthly/quarterly — no streaming needed |
| Database | **PostgreSQL** (SQLite acceptable for MVP) | Relational fits trade-flow star schema |
| Backend/API | Python (FastAPI) or Next.js API routes | Either fine; pick one, stay small |
| Frontend | **Next.js** | SSR for SEO on public map/category pages (organic acquisition) |
| Map | **MapLibre GL** or D3 choropleth with free GeoJSON | No Google Maps billing; choropleth is the whole need |
| CMS for Layer 3 | **Markdown files in the repo** (or a tiny admin form) | Requirement pages are documents; git history = free change log & audit trail |
| Alerts | Email via cheap transactional provider; Zalo OA phase 2 | |
| Hosting | Vercel/Netlify (frontend) + one small VPS (ETL + Postgres) | <$20/month total |

### 10.2 Data model (core tables)
```
hs_codes(hs6 PK, description_en, description_vi, synonyms[], category_slug, covered bool)
trade_flows(reporter, partner, hs6, period, flow ENUM(export,import),
            value_usd, quantity, qty_unit, source, published_date,
            PK(reporter, partner, hs6, period, flow))
signals(id, country, hs6, flow, period, yoy_delta, band, computed_at)
companies(id, name, country, role ENUM(buyer,seller), hs6[], profile_url,
          evidence_source, evidence_url, verified_date)
requirement_pages(id, hs6_group, market, body_md, last_full_review)
requirement_items(page_id, seq, text, type, mandatory, source_url, verified_date)
tenders(id, market, hs6, title, buyer_entity, deadline, url, scraped_at)
users(id, email, locale, tier)
watches(user_id, hs6, market, flow)
alerts(id, user_id, type ENUM(signal,tender,rule_change), payload, sent_at)
locked_page_clicks(user_id, hs6, market, clicked_at)   -- the roadmap oracle
```

### 10.3 Pipeline jobs
1. **Monthly:** pull national stats (Japan, Korea, EU, US) for covered HS codes; re-pull trailing 4 quarters (revisions); upsert `trade_flows`.
2. **Quarterly:** full Comtrade refresh for the global map (all countries, aggregate level).
3. **Daily:** tender scrapers for covered markets; diff against `tenders`; emit tender alerts.
4. **On publish:** requirement page edit → diff → emit rule-change alerts to watchers.
5. **After each data load:** recompute `signals` (pure SQL/pandas over `trade_flows`); band crossings vs. previous computation → emit signal alerts (weekly digest).

### 10.4 Non-functional
- Everything reproducible: raw pulls stored before transformation; signal computation is a pure function of stored data.
- Vietnamese + English UI from day one (i18n scaffolding, VN default).
- No login required for free tier browsing (SEO + zero-friction top of funnel); login required to watch.

---

## 11. Monetization

| | Free | Paid (single tier to start) |
|---|---|---|
| Global map + signals feed | ✔ | ✔ |
| Category & country drill-down | ✔ | ✔ |
| Buyer/seller profiles | 3 profiles visible, rest blurred | ✔ full |
| Qualification pages | Snapshot section only | ✔ full checklist + sources |
| Watches + alerts | 1 watch, weekly digest only | ✔ unlimited, instant tender & rule alerts |
| Tender feed | ✖ | ✔ |

- **Price hypothesis:** 200k–500k VND/month (~US$8–20) — SME-affordable, 10× under Volza. Test willingness in Stage 0 before fixing.
- Reality check baked in: SMEs pay for **leads and alerts**, not dashboards. The tender feed + alerts carry the paid tier; qualification depth justifies it; the map is marketing.

---

## 12. Validation plan — Stage 0 (non-negotiable, before any code)

**Build nothing until this passes.**

1. **Produce one manual report** (one weekend): "Wood Pellet Export Opportunities — [month]": active Korean/Japanese tenders, policy changes (Japan FIT/SBP status, Korea subsidy direction), reference prices, top-5 destination signals computed by hand from published stats, 10 certified foreign buyer profiles from FSC/SBP databases, and a 1-page "pellets → Japan" requirements checklist. Vietnamese language. PDF.
2. **Distribute to 20–30 exporters:** VIFOREST member companies, wood-industry Facebook/Zalo groups, direct email to company websites' contacts.
3. **Measure:** replies, follow-up questions, and the only question that matters — "would you pay [price] per month for this arriving automatically?"

**Go / kill criteria**
- **GO:** ≥5 substantive replies AND ≥3 people say yes to paying anything (even 100k VND/month) → build MVP (Phase 1).
- **PIVOT:** strong engagement but zero willingness to pay → test a different vertical (repeat Stage 0, ~1 week each) before concluding.
- **KILL:** <3 replies across two verticals → the market doesn't want this from an outsider; stop before writing code.

---

## 13. Roadmap

| Phase | Duration | Scope |
|---|---|---|
| **Stage 0** | 2–3 weeks | Manual report validation (§12). No code. |
| **Phase 1 — MVP** | 6–8 weeks | Global map (quarterly Comtrade) + pilot vertical full depth (signals, profiles, pellets→JP/KR/EU requirement pages) + watch/alerts (email) + locked pages + payments |
| **Phase 2** | +6 weeks | Second vertical (chosen from Stage 0 feedback + locked-page clicks), tender feed productized, Zalo alerts, monthly national-stats freshness for covered markets |
| **Phase 3** | ongoing | Markets/verticals strictly by locked-page telemetry; consider curated contact upgrade only if users demand it and manual verification is sustainable |

---

## 14. Risks & honest kill-list

| Risk | Severity | Mitigation |
|---|---|---|
| **Accuracy liability** — outdated requirement → user's container rejected at port | High | Source link + verified date on every item; "last full review" per page; disclaimer that official sources govern; change log |
| **Maintenance burden** — Layer 3 is a curation business, not software | High | Hard cap: ≤20 requirement pages until revenue; git-based workflow; quarterly review calendar |
| **Willingness-to-pay** — SMEs read free, don't pay | High | Stage 0 gate; alerts/tenders (not dashboards) carry the paid tier |
| **Churn after month 1** — look-up value extracted, user leaves | High | Watch/alert engine is the product; measure watches-per-user as the north-star metric |
| **Free-data commoditization** — anyone can rebuild Layer 1 | Medium | Accepted; Layer 1 is marketing. Moat = curated Layers 2–3 + Vietnamese localization |
| **Comtrade rate limits / API changes** | Medium | Cache raw pulls; national sources as primary for covered markets |
| **Signal noise despite floors** | Medium | Thresholds are config, not code; tune with real data in Phase 1 |
| **Scope creep back to "whole world"** | Medium | §3 scope is locked; locked-page telemetry is the only expansion mechanism |

---

## 15. Open questions (decide during Stage 0)
1. Final pilot-vertical choice if pellet exporters don't respond — tea, seafood, or cashew next?
2. Price point (200k vs 500k VND) — ask directly in Stage 0 conversations.
3. Brand name + domain (Vietnamese-friendly, trade-neutral).
4. Whether Vietnamese-reported (GDVC) or importer-reported figures headline the Vietnam tiles (recommendation: importer-reported per §6.4, but show both on drill-down).
5. Legal: terms-of-use disclaimer wording for requirement pages (information, not legal advice).
