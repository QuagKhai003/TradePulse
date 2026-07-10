/**
 * page.js — Layer-1 landing: demand map + signal feed + market tiles (plan §7.1).
 * @context  Server component. Reads the ETL snapshot and renders the whole Layer-1 screen SSR.
 *           Language via ?lang=en (VN default). Shows a SAMPLE banner while data is the fixture.
 * @done     Header (product + HS badge + honest period), choropleth, feed, tiles, disclaimer.
 * @todo     Product search (1.4), country drill-down (1.5), watch button (1.8).
 * @limits   Inform-never-match (Golden Rule): shows data only; no parties, no contacts.
 * @affects  Reads lib/snapshot; renders WorldMap + SignalFeed + MarketTile.
 */
import WorldMap from "./components/WorldMap.js";
import SignalFeed from "./components/SignalFeed.js";
import MarketTile from "./components/MarketTile.js";
import { loadSnapshot } from "./lib/snapshot.js";
import { t } from "./lib/i18n.js";

export default async function Page({ searchParams }) {
  const sp = searchParams ? await searchParams : {};
  const lang = sp.lang === "en" ? "en" : "vi";
  const tr = t(lang);
  const snap = await loadSnapshot();

  if (!snap) {
    return (
      <main className="page"><div className="empty">{tr.noData}</div></main>
    );
  }

  const product = lang === "en" ? snap.product.name_en : snap.product.name_vi;

  return (
    <main className="page">
      <header className="topbar">
        <div className="brand">
          <span className="logo">◈ TradePulse</span>
          <span className="tagline">{tr.tagline}</span>
        </div>
        <a className="langswitch" href={`?lang=${lang === "en" ? "vi" : "en"}`}>{tr.lang}</a>
      </header>

      {snap.is_sample && <div className="samplebar">⚠ {tr.sample}</div>}

      <section className="subhead">
        <h1>{tr.subtitle}</h1>
        <div className="chips">
          <span className="chip">{tr.product}: <strong>{product}</strong></span>
          <span className="chip hs">HS {snap.hs6}</span>
          <span className="chip">{tr.flowImport}</span>
          <span className="chip muted">{tr.period} {snap.latest_period}</span>
        </div>
      </section>

      <section className="grid">
        <div className="mapcol">
          <WorldMap markets={snap.markets} />
          <div className="markets">
            <h2>{tr.marketsTitle}</h2>
            <div className="tiles">
              {snap.markets.map((m) => <MarketTile key={m.slug} m={m} lang={lang} t={tr} />)}
            </div>
          </div>
        </div>
        <SignalFeed feed={snap.feed} lang={lang} t={tr} />
      </section>

      <footer className="disclaimer muted">{tr.disclaimer}</footer>
    </main>
  );
}
