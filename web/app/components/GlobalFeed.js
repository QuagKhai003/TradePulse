"use client";
/**
 * GlobalFeed.js — worldwide signal feed, both flows, filtered by the export/import toggle (plan §7.1).
 * @context  Each row: country + signed, colour-coded YoY % (the signal), then flow · value · magnitude
 *           · period. Direction = sign + colour + arrow, so a decline never reads as a rise. The flow
 *           toggle lives on the globe bar; SORT lives in this header. On desktop the list scrolls; on
 *           phones (≤820) it PAGINATES like the market feed (fixed page + "‹ n / N ›" pager below).
 * @limits   Presentation only; snapshot.feed is pre-sorted by severity then value. Pagination is
 *           client state (needs matchMedia).
 * @affects  Rendered on page.js (via HeroClient) from snapshot.feed + the active flow.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { bandArrow, bandLabel, fmtPct, fmtPeriod, fmtUSD, isFeedSignal, sigColor, slotFor } from "../lib/format.js";

const PER = 5;   // rows per page on mobile

export default function GlobalFeed({ countries, flow, freq = "A", lang, t, hs, sort = "none", tools }) {
  const [page, setPage] = useState(0);
  const [paged, setPaged] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(max-width: 820px)");
    const sync = () => setPaged(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);
  useEffect(() => { setPage(0); }, [flow, freq, hs, sort]);

  const nm = (x) => (lang === "en" ? x.name_en : x.name_vi) || "";
  const loc = lang === "en" ? "en" : "vi";
  const metric = flow === "export" ? "exp" : "imp";
  // Derive the feed from the countries at the chosen grain, so the M/Q/A toggle switches it too.
  const items = [];
  for (const c of countries) {
    const slot = slotFor(c[metric], freq);
    if (!slot || !isFeedSignal(slot.band)) continue;
    items.push({ code: c.code, name_en: c.name_en, name_vi: c.name_vi, flow,
                 value_usd: slot.value_usd, yoy_delta: slot.yoy_delta, band: slot.band,
                 direction: slot.direction, period: slot.period, estimated: slot.estimated });
  }
  // "none" is the state the app OPENS in: no re-sort at all — the feed keeps the snapshot's own order
  // (the ETL ships countries biggest-trader first), so nothing has been reordered behind the user's back.
  if (sort === "name-asc") items.sort((a, b) => nm(a).localeCompare(nm(b), loc));
  else if (sort === "name-desc") items.sort((a, b) => nm(b).localeCompare(nm(a), loc));
  else if (sort === "change-desc") items.sort((a, b) => (b.yoy_delta || 0) - (a.yoy_delta || 0));
  else if (sort === "change-asc") items.sort((a, b) => (a.yoy_delta || 0) - (b.yoy_delta || 0));
  else if (sort === "value-asc") items.sort((a, b) => (a.value_usd || 0) - (b.value_usd || 0));
  else if (sort === "value-desc") items.sort((a, b) => (b.value_usd || 0) - (a.value_usd || 0));

  const pageCount = Math.max(1, Math.ceil(items.length / PER));
  const cur = Math.min(page, pageCount - 1);
  const start = paged ? cur * PER : 0;
  const shown = paged ? items.slice(start, start + PER) : items;
  const filler = paged ? PER - shown.length : 0;

  return (
    <div className="col-fill">
      <div className="panel-h">
        <h2><b className="panel-n num">{items.length}</b> {t.feedTitle}</h2>
        {tools && <div className="panel-h-tools">{tools}</div>}
      </div>
      <ul className={`feed-list ${paged ? "feed-paged" : "scrollx"}`}>
        {shown.map((m, idx) => {
          const i = start + idx;
          const name = lang === "en" ? m.name_en : m.name_vi;
          const color = sigColor(m.band, m.direction, true);
          const flowLabel = m.flow === "export" ? t.exportsLabel : t.importsLabel;
          return (
            <li key={`${m.code}-${m.flow}-${i}`} className="feed-item">
              <div className="feed-row1">
                <Link className="feed-link" href={`/country/${m.code}?hs=${hs}${lang === "en" ? "&lang=en" : ""}`}>{name}</Link>
                <span className="feed-pct" style={{ color }}>{bandArrow(m.band, m.direction)} {fmtPct(m.yoy_delta)}</span>
              </div>
              <div className="feed-row2">
                <span className={`flowtag ${m.flow}`}>{flowLabel}</span>
                <span className="feed-val">{fmtUSD(m.value_usd)}</span>
                <span className="feed-band" style={{ color }}>{bandLabel(m.band, lang)}</span>
                <span className="muted">{fmtPeriod(m.period, lang)}{m.estimated ? ` · ${t.est}` : ""}</span>
              </div>
            </li>
          );
        })}
        {Array.from({ length: filler }).map((_, k) => (
          <li key={`fill-${k}`} className="feed-item feed-fill" aria-hidden="true">
            <div className="feed-row1">&nbsp;</div><div className="feed-row2">&nbsp;</div>
          </li>
        ))}
      </ul>
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
