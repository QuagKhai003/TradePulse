/**
 * EventsFeed.js — the qualification tab's regulatory feed (events lane, ADR-0007).
 * @context  Two kinds of signal, each given its own space so neither drowns the other:
 *           RULE CHANGES (WTO ePing SPS/TBT — what a market now requires) and BORDER REJECTIONS (EU
 *           RASFF — what is getting stopped, Vietnam-origin especially). Within each, THIS market's own
 *           entries come first, then global context. Each row cites its official source.
 * @limits   Public act + source link only (Golden Rule) — no party, no contact. Presentational.
 * @affects  Rendered by QualPanel. Data from lib/events.js (events-<hs>.json).
 */
const AREA = { TBT: "ev-tbt", SPS: "ev-sps" };
const CAP = 5;

function EventRow({ e, t, showMarket }) {
  const future = e.deadline && e.deadline >= new Date().toISOString().slice(0, 10);
  const isReject = e.kind === "rejection";
  const badgeCls = isReject ? "ev-reject" : (AREA[e.area] || "ev-oth");
  const badgeTxt = isReject ? t.evReject : (e.area || e.kind);
  return (
    <li className="ev-row">
      <span className="ev-date muted">{e.date || "—"}</span>
      <span className={`ev-area ${badgeCls}`}>{badgeTxt}</span>
      <span className="ev-body">
        <span className="ev-title">{e.title}</span>
        {isReject && e.detail ? <span className="ev-detail small">{e.detail}</span> : null}
        <span className="ev-meta muted small">
          {showMarket && e.market_name ? <>{e.market_name} · </> : null}
          {future ? <b className="ev-deadline">{t.qualDeadline} {e.deadline}</b> : null}
          {future ? " · " : null}
          {!isReject && <><span className={e.match === "hs" ? "ev-hs" : "ev-kw"}>
            {e.match === "hs" ? t.qualHsMatch : t.qualKwMatch}</span>{" · "}</>}
          <a href={e.url} target="_blank" rel="noopener noreferrer">
            {e.source === "eu-rasff" ? "EU RASFF ↗" : "WTO ePing ↗"}</a>
        </span>
      </span>
    </li>
  );
}

// This market's own entries first (its bar is moving), then the rest as context — order preserved
// (the ETL sorted newest-first), so a stable partition keeps recency within each group.
function partition(list, slug) {
  const here = [], elsewhere = [];
  for (const e of list) (slug && e.market === slug ? here : elsewhere).push(e);
  return here.concat(elsewhere).slice(0, CAP).map((e) => ({ e, isHere: slug && e.market === slug }));
}

function Block({ title, list, slug, t }) {
  if (!list.length) return null;
  return (
    <div className="ev-block">
      <div className="ev-group muted small">{title} <span className="ev-count">· {list.length}</span></div>
      <ul className="ev-list">
        {partition(list, slug).map(({ e, isHere }) => (
          <EventRow key={`${e.source}-${e.id}`} e={e} t={t} showMarket={!isHere} />
        ))}
      </ul>
    </div>
  );
}

export default function EventsFeed({ events, slug, marketName, t }) {
  const rules = events.filter((e) => e.kind !== "rejection");
  const rejects = events.filter((e) => e.kind === "rejection");
  return (
    <div className="ev-feed">
      <h3 className="ev-h">{t.qualChanges}</h3>
      <p className="muted small ev-sub">{t.qualChangesSub}</p>
      {events.length === 0 && <p className="muted small">{t.qualNoChanges}</p>}
      <Block title={t.qualRuleChanges} list={rules} slug={slug} t={t} />
      <Block title={t.qualRejections} list={rejects} slug={slug} t={t} />
    </div>
  );
}
