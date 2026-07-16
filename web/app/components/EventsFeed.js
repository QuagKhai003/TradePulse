/**
 * EventsFeed.js — the "Regulatory news" section body: two columns.
 * @context  RULE CHANGES (WTO ePing SPS/TBT — what a market is changing) and BORDER REJECTIONS (EU
 *           RASFF — what's getting stopped, Vietnam-origin especially). This market's own entries come
 *           first, then global context. Each entry is a light card (spacing, not divider lines); each
 *           cites its official source. The section heading lives on the page, not here.
 * @limits   Public act + source link only (Golden Rule) — no party, no contact. Presentational.
 * @affects  Rendered inside the Regulatory-news panel on country/[code]/page.js. Data lib/events.js.
 */
const AREA = { TBT: "ev-tbt", SPS: "ev-sps" };
const CAP = 5;

function EventItem({ e, t, showMarket }) {
  const future = e.deadline && e.deadline >= new Date().toISOString().slice(0, 10);
  const isReject = e.kind === "rejection";
  return (
    <li className="ev-item">
      <div className="ev-top">
        <span className={`ev-area ${isReject ? "ev-reject" : (AREA[e.area] || "ev-oth")}`}>
          {isReject ? t.evReject : (e.area || e.kind)}
        </span>
        <span className="ev-date muted">{e.date || "—"}</span>
      </div>
      <div className="ev-title">{e.title}</div>
      {isReject && e.detail ? <div className="ev-detail muted small">{e.detail}</div> : null}
      <div className="ev-meta muted small">
        {showMarket && e.market_name ? <>{e.market_name} · </> : null}
        {future ? <><b className="ev-deadline">{t.qualDeadline} {e.deadline}</b> · </> : null}
        <a href={e.url} target="_blank" rel="noopener noreferrer">
          {e.source === "eu-rasff" ? "EU RASFF ↗" : "Official WTO notice ↗"}
        </a>
      </div>
    </li>
  );
}

// This market's own entries first (its bar is moving), then the rest as context; ETL sorted newest-first.
function partition(list, slug) {
  const here = [], elsewhere = [];
  for (const e of list) (slug && e.market === slug ? here : elsewhere).push(e);
  return here.concat(elsewhere).slice(0, CAP).map((e) => ({ e, isHere: slug && e.market === slug }));
}

function Column({ title, sub, list, slug, t, tone }) {
  return (
    <div className={`ev-box ev-box-${tone}`}>
      <div className="ev-col-h">{title} <span className="ev-count">{list.length}</span></div>
      <p className="ev-col-sub muted small">{sub}</p>
      {list.length === 0
        ? <p className="muted small">—</p>
        : <ul className="ev-list">
            {partition(list, slug).map(({ e, isHere }) => (
              <EventItem key={`${e.source}-${e.id}`} e={e} t={t} showMarket={!isHere} />
            ))}
          </ul>}
    </div>
  );
}

export default function EventsFeed({ events, slug, marketName, t }) {
  if (!events.length) return null;
  const rules = events.filter((e) => e.kind !== "rejection");
  const rejects = events.filter((e) => e.kind === "rejection");
  return (
    <div className="ev-cols">
      <Column title={t.qualRuleChanges} sub={t.qualRuleSub} list={rules} slug={slug} t={t} tone="rules" />
      <Column title={t.qualRejections} sub={t.qualRejectSub} list={rejects} slug={slug} t={t} tone="rejects" />
    </div>
  );
}
