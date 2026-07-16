/**
 * PartnerTable.js — top partner countries with share + YoY (plan §7.3).
 * @context  "Japan pellet imports: Vietnam 55% ▲, Indonesia 20% ▲…". Vietnam row highlighted.
 *           Importer-reported for import flow, exporter-reported for export flow.
 * @limits   Presentation only.
 * @affects  Rendered by country/[code]/page.js.
 */
import { fmtPct, fmtUSD } from "../lib/format.js";

export default function PartnerTable({ partners, lang, t, col, vnCode = 704 }) {
  return (
    <table className="ptable">
      <thead>
        <tr><th>#</th><th>{col || t.partnerCountry}</th><th className="num">{t.value}</th>
          <th className="num">{t.share}</th><th className="num">{t.yoy}</th></tr>
      </thead>
      <tbody>
        {partners.map((p, i) => {
          const isVN = p.code === vnCode;
          const name = lang === "en" ? p.name_en : p.name_vi;
          const arrow = p.direction === "down" ? "▼" : p.direction === "up" ? "▲" : "";
          const color = p.direction === "down" ? "#b91c1c" : p.direction === "up" ? "#15803d" : "#64748b";
          return (
            <tr key={p.code} className={isVN ? "vnrow" : ""}>
              <td className="muted">{i + 1}</td>
              <td>{name}{isVN && <span className="vnflag"> ★</span>}</td>
              <td className="num">{fmtUSD(p.value_usd)}</td>
              <td className="num">{p.share != null ? `${(p.share * 100).toFixed(0)}%` : "—"}</td>
              <td className="num" style={{ color }}>{arrow} {p.yoy_delta != null ? fmtPct(p.yoy_delta) : "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
