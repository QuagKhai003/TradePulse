/**
 * SourcingChart.js — stacked-bar partner sourcing over quarters (plan §7.3).
 * @context  SSR SVG: each quarter is a stacked column of partner-country values, so an exporter
 *           sees how sourcing shifts. Vietnam's slice is outlined.
 * @limits   Presentation only; data is one flow's sourcing block. Local stable colours.
 * @affects  Rendered by country/[code]/page.js.
 */
const W = 640, H = 220, PAD = 8, PAD_TOP = 10, AXIS = 26;
const PALETTE = ["#0ea5e9", "#22c55e", "#f59e0b", "#a855f7", "#ef4444", "#14b8a6"];
const colorFor = (s, i) => (s.code === -1 ? "#cbd5e1" : PALETTE[i % PALETTE.length]);

export default function SourcingChart({ sourcing, lang, vnCode = 704 }) {
  const { periods, series } = sourcing;
  const totals = periods.map((_, i) => series.reduce((s, sr) => s + sr.values[i], 0));
  const maxTotal = Math.max(1, ...totals);
  const plotH = H - AXIS - PAD_TOP, plotW = W - PAD * 2;
  const colW = plotW / periods.length, barW = colW * 0.62;

  return (
    <div className="chart">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img" aria-label="Top partners by period">
        {periods.map((p, i) => {
          const x = PAD + i * colW + (colW - barW) / 2;
          let acc = 0;
          return (
            <g key={p}>
              {series.map((sr, si) => {
                const h = (sr.values[i] / maxTotal) * plotH;
                const y = PAD_TOP + plotH - acc - h;
                acc += h;
                if (h <= 0) return null;
                return <rect key={sr.code} x={x} y={y} width={barW} height={h} fill={colorFor(sr, si)}
                             stroke={sr.code === vnCode ? "#0f172a" : "none"} strokeWidth={sr.code === vnCode ? 1 : 0} />;
              })}
              <text x={x + barW / 2} y={H - 8} textAnchor="middle" className="chart-xlabel">{p.replace("-", " ")}</text>
            </g>
          );
        })}
      </svg>
      <ul className="chart-legend">
        {series.map((sr, si) => (
          <li key={sr.code}><span className="swatch" style={{ background: colorFor(sr, si) }} />
            {lang === "en" ? sr.name_en : sr.name_vi}</li>
        ))}
      </ul>
    </div>
  );
}
