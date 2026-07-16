# About TradePulse

## The one-line version

TradePulse is a demand-intelligence terminal for Vietnamese SME exporters. It answers three questions a factory owner actually asks — *Where is demand for my product moving? Who publicly buys it? What do I need to sell there?* — and it answers them without ever brokering a deal.

## The insight

Trade data is not scarce. UN Comtrade, government procurement portals, food-safety registries, WTO notifications — the raw material is public and free. What's scarce is a version of it a non-analyst can *act on*.

The incumbents (Volza, Panjiva, Tridge, ITC Trade Map) solved the wrong half of the problem. They built powerful databases and sold them to people whose job is querying databases. A wood-pellet mill owner in Bình Dương is not that person. They have a product, a container to fill, and a question — "is Japan still buying, and what does the paperwork look like?" — and no tool speaks their language, literally or figuratively.

TradePulse starts from the answer, not the database. A signal card that says *"Japanese wood-pellet imports up 9% year-over-year, Korea flat, EU cooling"* is worth more to that mill than a spreadsheet with ten million rows — even though the spreadsheet contains the signal card. The work is the compression, the plain language, the Vietnamese-first framing, and the sourcing.

## The positioning: inform, never match

The single most important design decision is what TradePulse **refuses** to do.

The moment a platform introduces a buyer to a seller, it inherits an enormous burden: verification, trust, dispute resolution, liability, and the entire adversarial dynamic of a marketplace where both sides have incentives to game it. That's why B2B marketplaces are so hard, and why "trade databases" hide behind analyst-priced subscriptions.

TradePulse sidesteps all of it by drawing a hard line: **it shows public information and it stops there.** Layer 2 lists a public buyer's *organisation name and the official record link* — the same thing you'd find yourself if you knew where the government publishes it — and never a private contact, an email, or a phone number. The user takes it from there.

This isn't a limitation the product apologizes for. It's the foundation. It's what lets every claim be verifiable, what keeps the operating cost near zero, and what makes the data trustworthy precisely because no one is being sold to.

## Two engineering commitments that ride under it

- **Deterministic signals only.** Every number the app displays is a reproducible formula over published data. A large language model never generates a figure a user sees. If a trend can't be computed, it isn't shown — no confident-sounding guesses about someone's livelihood.
- **Every requirement cites its source.** A wrong border requirement doesn't cost a click; it rejects a container. So each qualification item carries an official source link and a "last verified" date, or it doesn't ship. The Layer-3 content lives as markdown in the repo, which means git history is a free, tamper-evident audit trail of every requirement change.

## Why Vietnam, why now

Vietnam is one of the world's fastest-growing export economies, and the long tail of that growth is tens of thousands of SMEs who are excellent at production and under-served in market intelligence. They are the users who most need answers and least need another analyst tool. Starting Vietnamese-first, in a single pilot vertical (wood pellets and wood products) across five destination markets (Japan, Korea, EU, US, UK), keeps the scope honest and the sourcing verifiable before widening.

## What this repository is

A working Phase 1 MVP: a map-first Next.js app backed by a Python batch pipeline, running on real data across all three layers, covering 1,240 products and 226 reporter countries. It is a product prototype — the technology and the positioning are proven; willingness-to-pay is the next thing to test, not an assumption already made.

The stack is deliberately boring and cheap — Python standard library, SQLite, static JSON snapshots, a free-tier map — because the interesting part was never the infrastructure. It was deciding what *not* to build.
