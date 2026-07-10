/**
 * WorldMap.js — SSR choropleth of demand signals (Layer 1, plan §7.1).
 * @context  Server component: builds a static SVG world map with d3-geo + world-atlas, filling the
 *           covered destination markets by their signal band. No client JS — reliable + SEO-friendly.
 * @done     Natural-Earth projection; fills country markets (JP/KR/US/GB) by band; EU has no single
 *           polygon so it shows in the tiles/feed, not on the map (noted).
 * @todo     Hover tooltips + click-to-drill (client island) in batch 1.5.
 * @limits   Presentation only; colours come from lib/format. Reporter->ISO fixups live here.
 * @affects  Rendered by page.js; reads snapshot.markets.
 */
import { geoNaturalEarth1, geoPath } from "d3-geo";
import { feature } from "topojson-client";
import worldData from "world-atlas/countries-110m.json";
import { bandColor, MAP_NEUTRAL } from "../lib/format.js";

const W = 960;
const H = 460;

// Comtrade reporter code -> ISO-3166 numeric used by world-atlas (mostly identical; US differs).
const REPORTER_TO_ISO = { 392: "392", 410: "410", 842: "840", 826: "826" };

export default function WorldMap({ markets }) {
  const fc = feature(worldData, worldData.objects.countries);
  const projection = geoNaturalEarth1().fitSize([W, H], fc);
  const pathGen = geoPath(projection);

  // iso-numeric -> {color, market}
  const byIso = {};
  for (const m of markets) {
    const iso = REPORTER_TO_ISO[m.reporter];
    if (iso) byIso[iso] = m;
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="worldmap" role="img"
         aria-label="World demand map">
      <rect x="0" y="0" width={W} height={H} fill="transparent" />
      {fc.features.map((f) => {
        const m = byIso[String(f.id)];
        const fill = m ? bandColor(m.band, m.direction) : MAP_NEUTRAL;
        const d = pathGen(f);
        if (!d) return null;
        return (
          <path key={f.id} d={d} fill={fill}
                stroke={m ? "#0f172a" : "#d7dee8"} strokeWidth={m ? 0.8 : 0.3}>
            <title>{m ? `${m.name_en} — ${m.band}` : f.properties?.name}</title>
          </path>
        );
      })}
    </svg>
  );
}
