/**
 * PricePanel.js — the FORWARD lane: a product's world PRICE trend (ADR-0007).
 * @context  Sits as the third column of the key-figures card, matching the export/import rhythm:
 *           a quiet label, the year-on-year move as the hero number, then a tall area sparkline of the
 *           last ~24 months. A PRICE direction (demand-pressure cue), never the customs total.
 * @limits   Presentational; shown only when the product has an honest IMF series (loader -> null).
 * @affects  Rendered inside FlowStrip on country/[code]/page.js. Data from lib/forward.js.
 */
const DIR = { up: { cls: "fwd-up", a: "▲" }, down: { cls: "fwd-down", a: "▼" }, flat: { cls: "fwd-flat", a: "▬" } };

function Spark({ series }) {
  const vals = series.map((s) => s.value);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const n = series.length, H = 52;
  const at = (v, i) => [(i / (n - 1)) * 100, H - ((v - lo) / span) * (H - 8) - 4];
  const pts = series.map((s, i) => at(s.value, i).map((x) => x.toFixed(2)).join(",")).join(" ");
  const last = at(series[n - 1].value, n - 1);
  return (
    <svg className="fwd-spark" viewBox={`0 0 100 ${H}`} preserveAspectRatio="none" aria-hidden="true">
      <polygon className="fwd-area" points={`0,${H} ${pts} 100,${H}`} />
      <polyline points={pts} fill="none" strokeWidth="1.6" vectorEffect="non-scaling-stroke" />
      <circle cx={last[0]} cy={last[1]} r="2" />
    </svg>
  );
}

export default function PricePanel({ forward, lang, t }) {
  if (!forward) return null;
  const d = DIR[forward.direction] || DIR.flat;
  const label = lang === "en" ? forward.label_en : forward.label_vi;
  const yoy = forward.yoy_pct == null ? "—" : `${forward.yoy_pct > 0 ? "+" : ""}${forward.yoy_pct}%`;
  const from = forward.series[0]?.period;
  return (
    <div className={`panel fwd ${d.cls}`}>
      <h2>{t.fwdTitle}</h2>
      <div className="bigval fwd-big">{d.a} {yoy}<span className="fwd-unit"> {t.fwdYoY}</span></div>
      <div className="bigmeta"><span className="muted">{label}</span></div>
      <Spark series={forward.series} />
      <p className="muted small fwd-meta">
        {from} – {forward.latest_period} · {t.fwdSub} ·{" "}
        <a href={forward.url} target="_blank" rel="noopener noreferrer">IMF PCPS ↗</a>
      </p>
    </div>
  );
}
