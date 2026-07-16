/**
 * PsdPanel.js — the FORWARD OUTLOOK lane: USDA PSD supply/demand forecast for a market (ADR-0007).
 * @context  A forecast, not a customs figure: what a market is expected to produce, import, export,
 *           consume, and hold in stock next market year. Shows the VIEWED market when PSD covers it,
 *           else the World balance (a supply/demand cue that still helps). A SEPARATE lane — quantities,
 *           never merged into the customs $ signal.
 * @limits   Presentational; shown only for ag commodities PSD covers (loader -> null otherwise).
 * @affects  Rendered on country/[code]/page.js. Data from lib/psd.js. Source: USDA PSD (cited).
 */
const DIR = { up: "psd-up", down: "psd-down", flat: "psd-flat" };
const ARROW = { up: "▲", down: "▼", flat: "▬" };

function fmtQty(v) {
  return v == null ? "—" : Math.round(v).toLocaleString("en-US");
}

function myLabel(y) {
  const n = Number(y);
  return Number.isFinite(n) ? `${n}/${String(n + 1).slice(2)}` : y;   // 2025 -> 2025/26
}

export default function PsdPanel({ psd, code, marketName, lang, t }) {
  if (!psd) return null;
  const forMarket = psd[String(code)];
  const block = forMarket || psd["0"];              // fall back to the World balance
  if (!block || !block.attributes?.length) return null;
  const isWorld = !forMarket;
  const who = isWorld ? t.psdWorld : marketName;
  return (
    <div className="panel psd">
      <div className="psd-head">
        <h3 className="psd-title">{who} · {t.psdMY} {myLabel(block.market_year)}</h3>
        <span className="muted small psd-unit">{block.unit}</span>
      </div>
      <table className="psd-table">
        <tbody>
          {block.attributes.map((a) => {
            const name = lang === "en" ? a.en : a.vi;
            const dir = a.direction || "flat";
            const yoy = a.yoy == null ? "" : `${a.yoy > 0 ? "+" : ""}${a.yoy}%`;
            return (
              <tr key={a.id}>
                <td className="psd-attr">{name}</td>
                <td className="psd-val num">{fmtQty(a.latest)}</td>
                <td className={`psd-yoy num ${DIR[dir]}`}>{a.yoy == null ? "" : `${ARROW[dir]} ${yoy}`}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="muted small psd-foot">
        {isWorld ? t.psdWorldNote : t.psdSub} ·{" "}
        <a href={block.url} target="_blank" rel="noopener noreferrer">USDA PSD ↗</a>
      </p>
    </div>
  );
}
