/**
 * country/[code]/loading.js — instant navigation skeleton for the country drill-down.
 * @context  The country page does real server work per request (snapshot + tenders + sellers + orders +
 *           cpv + forward + events, read fresh so re-running the ETL shows up without a rebuild). In dev
 *           that render is ~1–4s, so clicking a country on the globe felt like a hang. App Router streams
 *           THIS the instant the link is clicked and swaps in the page when it's ready — the click now
 *           gives immediate feedback instead of a frozen globe.
 * @limits   Pure presentation, no data. Mirrors the real page's cpage layout (summary + three sections)
 *           so the swap doesn't jump. Styles are the .cskel* shimmer rules in globals.css.
 * @affects  Rendered automatically by Next between navigation and country/[code]/page.js resolving.
 */
export default function CountryLoading() {
  return (
    <main className="page cpage" aria-busy="true">
      <div className="cskel-back cskel" />
      <section className="csum">
        <div className="csum-id">
          <div className="cskel cskel-h1" />
          <div className="cskel-meta">
            <span className="cskel cskel-chip" />
            <span className="cskel cskel-chip" />
            <span className="cskel cskel-chip wide" />
          </div>
        </div>
      </section>

      {["", "", ""].map((_, i) => (
        <div key={i} className="cskel-sec">
          <div className="cskel cskel-sech" />
          <div className="cskel cskel-card" />
        </div>
      ))}
    </main>
  );
}
