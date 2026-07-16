/**
 * country/[code]/page.js — country drill-down: its export + import signals, then deeper links.
 * @context  Click a country on the map/feed -> this view: both-flow value + YoY band + history, plus
 *           links to the qualification page (if covered) and the profiles directory (plan §7.3–7.5).
 * @limits   Inform-never-match; value/volume only.
 * @affects  Reads lib/snapshot; renders WatchButton.
 */
import Link from "next/link";
import SearchBox from "../../components/SearchBox.js";
import BrowseCountries from "../../components/BrowseCountries.js";
import WatchButton from "../../components/WatchButton.js";
import PartnerTable from "../../components/PartnerTable.js";
import SourcingChart from "../../components/SourcingChart.js";
import QualPanel from "../../components/QualPanel.js";
import PricePanel from "../../components/PricePanel.js";
import PsdPanel from "../../components/PsdPanel.js";
import FlowStrip from "../../components/FlowStrip.js";
import MarketFeed from "../../components/MarketFeed.js";
import EventsFeed from "../../components/EventsFeed.js";
import { loadSnapshot } from "../../lib/snapshot.js";
import { loadForward } from "../../lib/forward.js";
import { loadPsd } from "../../lib/psd.js";
import { loadEvents, MARKET_SLUG } from "../../lib/events.js";
import { loadSourcing } from "../../lib/sourcing.js";
import { loadAwards, loadCpvMatch, loadSellers, loadTenders } from "../../lib/tenders.js";
import { resolveLang, t, VI_ENABLED } from "../../lib/i18n.js";

export default async function CountryPage({ params, searchParams }) {
  const { code } = await params;
  const sp = searchParams ? await searchParams : {};
  const lang = resolveLang(sp.lang);
  const tr = t(lang);
  const snap = await loadSnapshot(sp.hs);
  const hs = (snap && snap.hs6) || sp.hs || "440131";
  const qs = `?hs=${hs}${lang === "en" ? "&lang=en" : ""}`;
  const backHome = `/?hs=${hs}${lang === "en" ? "&lang=en" : ""}`;
  const c = snap?.countries.find((x) => String(x.code) === String(code));

  // Switching product from THIS page can land on a product the country doesn't trade — that's a normal
  // empty state, not a 404. Keep the header + search so the user can pick another product right here.
  if (snap && !c) {
    const prod = lang === "en" ? snap.product.name_en : snap.product.name_vi;
    return (
      <main className="page cpage">
        <header className="topbar topbar-country">
          <div className="brand"><Link className="logo" href={backHome}>◈ TradePulse</Link></div>
          <div className="hero-search-top hero-search-top--light">
            <SearchBox lang={lang} placeholder={tr.searchHere} countryCode={code} />
            <BrowseCountries countries={snap.countries} lang={lang} hs={hs} label={tr.browseCountry} />
          </div>
          {VI_ENABLED && <a className="langswitch" href={`?lang=${lang === "en" ? "vi" : "en"}`}>{tr.lang}</a>}
        </header>
        <Link className="back" href={backHome}>{tr.backMap}</Link>
        <div className="empty">{tr.noCountryProduct} <b>{prod}</b>.</div>
      </main>
    );
  }
  if (!snap || !c) return <main className="page cpage"><div className="empty">404 · <Link href={backHome}>{tr.backMap}</Link></div></main>;

  const name = lang === "en" ? c.name_en : c.name_vi;
  const product = lang === "en" ? snap.product.name_en : snap.product.name_vi;
  const isPellets = hs === "440131";
  // Load everything for this product IN PARALLEL — these were ~8 sequential file reads, which made
  // navigating to a country feel slow. They're independent, so fan them out.
  const [sourcingAll, allTenders, allSellers, allOrders, cpv, forward, qualEvents, psd] = await Promise.all([
    loadSourcing(hs), loadTenders(hs), loadSellers(hs), loadAwards(hs),
    loadCpvMatch(hs), loadForward(hs), loadEvents(hs), loadPsd(hs),
  ]);
  const sourcing = sourcingAll?.[String(c.code)] || null;
  const qualSlug = MARKET_SLUG[Number(c.code)] || null;   // regulatory news section
  // Market-SPECIFIC buyers/orders: the feed now shows only THIS country's own public buyers, from that
  // market's procurement source (EU→TED, US→USAspending, UK→OCDS, KR→KONEPS, +OCDS nations). A country
  // with no source shows an empty feed (honest) rather than a foreign market's buyers. The EU aggregate
  // (97) is the one many-country view — it shows all EU-member notices.
  const isEUagg = String(c.code) === "97";
  const feedTenders = isEUagg ? allTenders : allTenders.filter((x) => String(x.buyer_code) === String(c.code));
  const feedOrders = isEUagg ? allOrders
    : allOrders.filter((x) => String(x.buyer_code) === String(c.code) || String(x.seller_code) === String(c.code));
  // Sellers come from approval registries (EU DG SANTE) — this country's own only.
  const sellersHere = isEUagg ? allSellers : allSellers.filter((x) => String(x.seller_code) === String(c.code));
  const openCount = Infinity;   // no paywall — all parties visible, nothing blurred
  // The country's OWN latest period — not the snapshot-wide max (which would read as a lie next to an
  // earlier-year figure).
  const asOf = [c.exp?.period, c.imp?.period].filter(Boolean).sort().pop() || snap.latest_period;
  const asOfEst = (c.exp?.period === asOf && c.exp?.estimated) || (c.imp?.period === asOf && c.imp?.estimated);

  return (
    <main className="page cpage">
      {/* header mirrors the globe's layout — search + browse centered — but with country-page behaviour:
          search stays on THIS country (swaps product), browse jumps to ANOTHER country (keeps product). */}
      <header className="topbar topbar-country">
        <div className="brand"><Link className="logo" href={backHome}>◈ TradePulse</Link></div>
        <div className="hero-search-top hero-search-top--light">
          <SearchBox lang={lang} placeholder={tr.searchHere} countryCode={c.code} />
          <BrowseCountries countries={snap.countries} lang={lang} hs={hs} label={tr.browseCountry} />
        </div>
        {VI_ENABLED && <a className="langswitch" href={`?lang=${lang === "en" ? "vi" : "en"}`}>{tr.lang}</a>}
      </header>

      <Link className="back" href={backHome}>{tr.backMap}</Link>

      {snap.is_sample && <div className="samplebar">⚠ {tr.sample}</div>}

      {/* SUMMARY — identity + the three key figures (exports · imports · world price) in one strip,
          so "how is demand moving" reads at a glance instead of being scattered down the page. */}
      <section className="csum">
        <div className="csum-id">
          <h1>{name} · {product}</h1>
          <div className="csum-meta">
            <span className="chip hs">HS {snap.hs6}</span>
            <span className="chip muted">{tr.asOf} {asOf}{asOfEst ? ` · ${tr.est}` : ""}</span>
            <WatchButton watchKey={`signal:${snap.hs6}:${c.code}`} meta={{ hs6: snap.hs6, market: String(c.code), kind: "signal" }}
                         labelOff={tr.watch} labelOn={tr.watching} />
            {isPellets && <a className="chip link" href={`/profiles${lang === "en" ? "?lang=en" : ""}`}>{tr.profilesLink}</a>}
          </div>
        </div>
      </section>

      {/* big bold section titles sit OUTSIDE the cards, on the space. Three sections: the trade + price
          figures, who is in the market, and what it takes to sell here. */}
      <h2 className="csec-h">{tr.secTrade}</h2>
      {/* ONE card for the whole trade picture: the export/import figures + world price on top, then the
          partner-country tables below (passed as `below`). Partners are named from THIS country's side —
          its export partners are the ones it sells TO, its import partners the ones it buys FROM. */}
      <FlowStrip exp={c.exp} imp={c.imp} lang={lang} t={tr}
                 below={sourcing && ["export", "import"].map((fl) => sourcing[fl] && (
                   <section key={fl} className="sourcing-sec">
                     <h2>{fl === "export" ? tr.exportPartners : tr.importPartners}
                       <span className="muted src-grain">– {(sourcing[fl].periods || []).some((p) => p.includes("Q")) ? tr.quarterly : tr.annual}</span>
                       <span className="src-dir">({fl === "export" ? tr.sellTo : tr.buyFrom})</span></h2>
                     <div className="drillgrid">
                       <div className="panel"><PartnerTable partners={sourcing[fl].partners} lang={lang} t={tr} col={tr.partnerCol} /></div>
                       <div className="panel"><SourcingChart sourcing={sourcing[fl]} lang={lang} /></div>
                     </div>
                   </section>
                 ))}>
        <PricePanel forward={forward} lang={lang} t={tr} />
      </FlowStrip>

      {/* FORWARD OUTLOOK lane (ADR-0007): USDA PSD supply/demand forecast — ag products only, its own
          section so it never reads as a customs number. Shows this market, or the World balance. */}
      {psd && (
        <>
          <h2 className="csec-h">{tr.secOutlook}</h2>
          <PsdPanel psd={psd} code={c.code} marketName={name} lang={lang} t={tr} />
        </>
      )}

      <h2 className="csec-h">{tr.marketFeed}</h2>
      <MarketFeed tenders={feedTenders} sellers={sellersHere} orders={feedOrders}
                  product={product} country={name} cpv={cpv} hs={hs} lang={lang} t={tr}
                  openCount={openCount} />

      {/* "All products" (TOTAL) has no meaningful per-product qualification -> show only regulatory news. */}
      {hs !== "TOTAL" && (
        <>
          <h2 className="csec-h">{tr.qualTitle}</h2>
          <QualPanel hs={hs} code={c.code} product={product} country={name} lang={lang} t={tr} />
        </>
      )}

      {qualEvents.length > 0 && (
        <>
          <h2 className="csec-h">{tr.qualRegWatch}</h2>
          <EventsFeed events={qualEvents} slug={qualSlug} marketName={name} t={tr} />
        </>
      )}

      <footer className="disclaimer muted">{tr.disclaimer}</footer>
    </main>
  );
}
