/**
 * SignalFeed.js — the moderate+ signal feed (plan §7.1 side panel).
 * @context  Push-worthy signals only (band >= moderate), already sorted by severity then value in
 *           the snapshot. Each row = a plain-language "what moved" line an exporter can act on.
 * @limits   Presentation only.
 * @affects  Rendered on page.js from snapshot.feed.
 */
import { bandArrow, bandColor, bandLabel, fmtPct, fmtUSD } from "../lib/format.js";

export default function SignalFeed({ feed, lang, t }) {
  return (
    <aside className="feed">
      <h2>{t.feedTitle}</h2>
      <p className="feed-note muted">{t.feedNote}</p>
      {feed.length === 0 && <p className="muted">—</p>}
      <ul>
        {feed.map((m) => {
          const name = lang === "en" ? m.name_en : m.name_vi;
          return (
            <li key={m.slug} className="feed-item">
              <span className="dot" style={{ background: bandColor(m.band, m.direction) }} />
              <div className="feed-body">
                <div className="feed-top">
                  <strong>{name}</strong>
                  <span className="feed-band" style={{ color: bandColor(m.band, m.direction) }}>
                    {bandArrow(m.band, m.direction)} {bandLabel(m.band, lang)}
                  </span>
                </div>
                <div className="feed-sub muted">
                  {fmtUSD(m.value_usd)} · {fmtPct(m.yoy_delta)} {t.yoy} · {m.period}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
