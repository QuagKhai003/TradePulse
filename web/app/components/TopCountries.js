"use client";
/**
 * TopCountries.js — countries ranked by total trade: export + import volume + YoY% (plan §7.1).
 * @context  ALL countries, ranked by the shown flow's value. On desktop the list scrolls inside the
 *           panel; on phones (≤820) it PAGINATES like the country-page market feed — a fixed page of
 *           rows + a "‹ n / N ›" pager below — so the whole list is reachable without one long scroll.
 *           XK (export) / NK (import) shown as colour tags; YoY colour = green rising / red falling.
 * @limits   Presentation only; value/volume only. Pagination is client state (needs matchMedia).
 * @affects  Rendered in the left overlay panel on page.js (via HeroClient).
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { fmtPct, fmtUSD, sigColor, slotFor } from "../lib/format.js";

const PER = 5;   // rows per page on mobile

function Flow({ tag, cls, slot }) {
  if (!slot) return <span className="tcf"><i className={`tcf-tag ${cls}`}>{tag}</i><b className="tcf-val num">—</b><em /></span>;
  const c = sigColor(slot.band, slot.direction, true);
  return (
    <span className="tcf">
      <i className={`tcf-tag ${cls}`}>{tag}</i>
      <b className="tcf-val num">{fmtUSD(slot.value_usd)}</b>
      <em className="tcf-pct num" style={{ color: c }}>{slot.yoy_delta != null ? fmtPct(slot.yoy_delta) : ""}</em>
    </span>
  );
}

export default function TopCountries({ countries, lang, t, hs, freq = "A", flow = "import" }) {
  const [page, setPage] = useState(0);
  // Paginate on phones, scroll on desktop. matchMedia in an effect so the server render (all rows)
  // matches the first client render, then upgrades to paged on mobile — no hydration mismatch.
  const [paged, setPaged] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 820px)");
    const sync = () => setPaged(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);
  // Reset to the first page when the ranking changes underneath (flow/grain/product).
  useEffect(() => { setPage(0); }, [flow, freq, hs]);

  // Rank by the flow currently shown on the globe (import or export), NOT export+import combined —
  // otherwise, viewing imports, a huge EXPORTER (Saudi crude) still ranks near the top with a tiny
  // import, which reads as a wrong order. The ranking now matches the globe + the flow toggle.
  const metric = flow === "export" ? "exp" : "imp";
  const rank = (c) => slotFor(c[metric], freq)?.value_usd || 0;
  const rows = [...countries].sort((a, b) => rank(b) - rank(a));
  // The period the ranking is FOR — the latest one present at the chosen grain.
  const asOf = rows.map((c) => slotFor(c[metric], freq)?.period).filter(Boolean).sort().pop();

  const pageCount = Math.max(1, Math.ceil(rows.length / PER));
  const cur = Math.min(page, pageCount - 1);
  const start = paged ? cur * PER : 0;
  const shown = paged ? rows.slice(start, start + PER) : rows;
  const filler = paged ? PER - shown.length : 0;   // pad the short last page so the box keeps one height

  return (
    <div className="col-fill">
      <div className="panel-h"><h2>{t.topCountries}</h2>{asOf && <span className="tc-period">{t.inPeriod} {asOf}</span>}</div>
      <ol className={`tc-list ${paged ? "tc-paged" : "scrollx"}`}>
        {shown.map((c, idx) => {
          const i = start + idx;
          return (
            <li key={c.code} className="tc-row">
              <Link className="tc-link" href={`/country/${c.code}?hs=${hs}${lang === "en" ? "&lang=en" : ""}`}>
                <span className="tc-rank num">{i + 1}</span>
                <span className="tc-name">{lang === "en" ? c.name_en : c.name_vi}</span>
                <span className="tc-flows">
                  <Flow tag={t.exportsShort} cls="export" slot={slotFor(c.exp, freq)} />
                  <Flow tag={t.importsShort} cls="import" slot={slotFor(c.imp, freq)} />
                </span>
              </Link>
            </li>
          );
        })}
        {Array.from({ length: filler }).map((_, k) => (
          <li key={`fill-${k}`} className="tc-row tc-fill" aria-hidden="true">
            <span className="tc-link">
              <span className="tc-rank">&nbsp;</span><span className="tc-name">&nbsp;</span>
              <span className="tc-flows"><span className="tcf">&nbsp;</span><span className="tcf">&nbsp;</span></span>
            </span>
          </li>
        ))}
      </ol>
      {paged && pageCount > 1 && (
        <nav className="col-pager">
          <button type="button" disabled={cur === 0} onClick={() => setPage(cur - 1)} aria-label="Previous">‹</button>
          <span className="col-page num">{cur + 1} / {pageCount}</span>
          <button type="button" disabled={cur >= pageCount - 1} onClick={() => setPage(cur + 1)} aria-label="Next">›</button>
        </nav>
      )}
    </div>
  );
}
