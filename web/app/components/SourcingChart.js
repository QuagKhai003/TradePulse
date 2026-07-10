/**
 * SourcingChart.js — stacked-bar sourcing over time (plan §7.3 "who sourced from where").
 * @context  SSR SVG (no client JS): each quarter is a stacked column of partner-country values,
 *           so an exporter sees how sourcing shifts. Straight query on free bilateral data.
 * @limits   Presentation only; data is snapshot.sourcing. Colours are local + stable by order.
 * @affects  Rendered by market/[slug]/page.js.
 */
const W = 640, H = 240, PAD = 8, PAD_TOP = 10, AXIS = 26;
const PALETTE = ["#0ea5e9", "#22c55e", "#f59e0b", "#a855f7", "#ef4444", "#14b8a6"];

function colorFor(series, i) {
  return series.code === -1 ? "#cbd5e1" : PALETTE[i % PALETTE.length];
}

export default function SourcingChart({ sourcing, lang, vnCode = 704 }) {
  const { periods, series } = sourcing;
  const totals = periods.map((_, i) => series.reduce((s, srp) => s + srp.values[i], 0));
  const maxTotal = Math.max(1, ...totals);
  const plotH = H - AXIS - PAD_TOP;
  const plotW = W - PAD * 2;
  const colW = plotW / periods.length;
  const barW = colW * 0.62;

  return (
    <div className="chart">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img" aria-label="Sourcing over time">
        {periods.map((p, i) => {
          const x = PAD + i * colW + (colW - barW) / 2;
          let acc = 0;
          return (
            <g key={p}>
              {series.map((srp, si) => {
                const v = srp.values[i];
                const h = (v / maxTotal) * plotH;
                const y = PAD_TOP + plotH - acc - h;
                acc += h;
                if (h <= 0) return null;
                return <rect key={srp.code} x={x} y={y} width={barW} height={h}
                             fill={colorFor(srp, si)} stroke={srp.code === vnCode ? "#0f172a" : "none"}
                             strokeWidth={srp.code === vnCode ? 1 : 0} />;
              })}
              <text x={x + barW / 2} y={H - 8} textAnchor="middle" className="chart-xlabel">{p}</text>
            </g>
          );
        })}
      </svg>
      <ul className="chart-legend">
        {series.map((srp, si) => (
          <li key={srp.code}>
            <span className="swatch" style={{ background: colorFor(srp, si) }} />
            {lang === "en" ? srp.name_en : srp.name_vi}
          </li>
        ))}
      </ul>
    </div>
  );
}
