/**
 * Legend.js — map colour key (ui-ux-pro-max #37: never convey info by colour alone).
 * @context  The choropleth colours countries by signal direction; this names what the colours mean.
 * @limits   Presentation only.
 * @affects  Rendered in the map panel header on page.js.
 */
import { MAP_NEUTRAL } from "../lib/format.js";

export default function Legend({ lang }) {
  const items = lang === "en"
    ? [["#15803d", "Rising"], ["#b91c1c", "Falling"], ["#7c3aed", "New lane"], [MAP_NEUTRAL, "No data"]]
    : [["#15803d", "Đang tăng"], ["#b91c1c", "Đang giảm"], ["#7c3aed", "Tuyến mới"], [MAP_NEUTRAL, "Chưa có"]];
  return (
    <div className="legend">
      {items.map(([c, l]) => (
        <span key={l} className="legend-item"><span className="legend-dot" style={{ background: c }} />{l}</span>
      ))}
    </div>
  );
}
