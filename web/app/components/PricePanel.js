/**
 * PricePanel.js — the FORWARD lane: a product's world PRICE trend (ADR-0007).
 * @context  Customs value says where demand WENT; a moving world price is a live demand-pressure cue.
 *           Shown BESIDE the flow panels, clearly a PRICE direction (not a volume forecast, not the
 *           customs total). Rising price = firmer demand for a seller. Server-rendered SVG sparkline.
 * @limits   Presentational. Only shown when the product has an honest IMF series (loader returns null
 *           otherwise). Deterministic — the shape is the published monthly series, nothing inferred.
 * @affects  Rendered by country/[code]/page.js. Data from lib/forward.js (forward-<hs>.json).
 */
const DIR = { up: { cls: "fwd-up", a: "▲" }, down: { cls: "fwd-down", a: "▼" }, flat: { cls: "fwd-flat", a: "▬" } };

function Spark({ series }) {
  const vals = series.map((s) => s.value);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const n = series.length;
  const pts = series.map((s, i) => {
    const x = (i / (n - 1)) * 100;
    const y = 26 - ((s.value - lo) / span) * 24 - 1;   // 1..25, inverted (SVG y-down)
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
  const last = pts.split(" ").pop().split(",");
  return (
    <svg className="fwd-spark" viewBox="0 0 100 26" preserveAspectRatio="none" aria-hidden="true">
      <polyline points={pts} fill="none" strokeWidth="1.4" vectorEffect="non-scaling-stroke" />
      <circle cx={last[0]} cy={last[1]} r="1.8" />
    </svg>
  );
}

export default function PricePanel({ forward, lang, t }) {
  if (!forward) return null;
  const d = DIR[forward.direction] || DIR.flat;
  const label = lang === "en" ? forward.label_en : forward.label_vi;
  const yoy = forward.yoy_pct == null ? "—" : `${forward.yoy_pct > 0 ? "+" : ""}${forward.yoy_pct}%`;
  return (
    <div className={`panel fwd ${d.cls}`}>
      <h2>{t.fwdTitle} <span className="muted">· {label}</span></h2>
      <div className="fwd-row">
        <div className="fwd-yoy">
          <span className="fwd-arrow">{d.a}</span> <span className="fwd-pct">{yoy}</span>
          <span className="muted small"> {t.fwdYoY}</span>
        </div>
        <Spark series={forward.series} />
      </div>
      <p className="muted small fwd-meta">
        {t.fwdSub} · {t.asOf} {forward.latest_period} ·{" "}
        <a href={forward.url} target="_blank" rel="noopener noreferrer">IMF PCPS ↗</a>
      </p>
    </div>
  );
}
