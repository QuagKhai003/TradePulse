/**
 * GlobalFeed.js — worldwide signal feed, both flows, filtered by the export/import/all toggle.
 * @context  Side panel (plan §7.1). Each row leads with the country + a signed, colour-coded YoY %
 *           (the signal), then a muted subline: flow · value · magnitude · period. Direction is
 *           carried by sign + colour + arrow, so a decline never reads as a rise.
 * @limits   Presentation only; snapshot.feed is pre-sorted by severity then value.
 * @affects  Rendered on page.js from snapshot.feed + the active flow.
 */
import Link from "next/link";
import { bandArrow, bandLabel, fmtPct, fmtUSD, sigColor } from "../lib/format.js";

export default function GlobalFeed({ feed, flow, lang, t, hs }) {
  const items = flow === "all" ? feed : feed.filter((f) => f.flow === flow);
  return (
    <aside className="feed">
      <div className="feed-head">
        <h2>{t.feedTitle}</h2>
        <span className="feed-count">{items.length}</span>
      </div>
      <p className="feed-note muted">{t.feedNote}</p>
      {items.length === 0 && <p className="muted">—</p>}
      <ul>
        {items.map((m, i) => {
          const name = lang === "en" ? m.name_en : m.name_vi;
          const color = sigColor(m.band, m.direction);
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
                <span className="muted">{m.period}</span>
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
