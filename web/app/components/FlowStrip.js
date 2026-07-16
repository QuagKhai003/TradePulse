"use client";
/**
 * FlowStrip.js — the country page's key-figures card: exports · imports · world price, with a
 * Year/Quarter toggle at the top (client island so the grain can switch without a reload).
 * @context  Each flow slot carries its non-default grains in by_freq (see lib/snapshot). The toggle
 *           swaps the annual slot for the quarterly one; Quarter greys out when a product has no
 *           quarterly data. Text toggle, not pills — the chosen word colours in, hover glows.
 * @limits   Presentational; pure over the slots. PricePanel comes in as children (a 3rd figures column);
 *           the partner-sourcing blocks come in as `below` and render full-width UNDER the figures, so
 *           the whole trade picture is ONE card instead of separate boxes stacked down the page.
 * @affects  Rendered by country/[code]/page.js. Uses lib/format (pure).
 */
import { useState } from "react";
import { bandArrow, bandColor, bandLabel, fmtPct, fmtPeriod, fmtUSD } from "../lib/format.js";

function pick(slot, freq) {
  if (!slot) return null;
  return freq === "A" ? slot : (slot.by_freq?.[freq] || null);
}

function Stat({ title, slot, t, lang }) {
  if (!slot) return <div className="panel"><h2>{title}</h2><p className="muted">—</p></div>;
  const color = bandColor(slot.band, slot.direction);
  const hasSig = slot.band && slot.band !== "none";
  const hist = slot.history || [];
  const max = Math.max(1, ...hist.map((h) => h.value_usd));
  return (
    <div className="panel">
      <h2>{title}</h2>
      <div className="bigval">{fmtUSD(slot.value_usd)}</div>
      <div className="bigmeta">
        {hasSig
          ? <span className="cband" style={{ color }}>{bandArrow(slot.band, slot.direction)} {bandLabel(slot.band, lang)} · {fmtPct(slot.yoy_delta)}</span>
          : <span className="muted">{t.noSignal}</span>}
        <span className="muted"> · {fmtPeriod(slot.period, lang)}</span>
        {slot.estimated && <span className="est-tag" title={t.estTip}>{t.est}</span>}
      </div>
      {hist.length > 1 && <div className="spark">
        {hist.map((h) => (
          <div key={h.period} className="spark-bar" title={`${h.period}: ${fmtUSD(h.value_usd)}`}>
            <span className="spark-val num">{fmtUSD(h.value_usd)}</span>
            <div style={{ height: `${Math.round((h.value_usd / max) * 82)}%`, background: color }} />
            <span className="spark-x muted">{h.period.replace("-", " ")}</span>
          </div>
        ))}
      </div>}
    </div>
  );
}

export default function FlowStrip({ exp, imp, lang, t, children, below }) {
  const hasQ = !!(exp?.by_freq?.Q || imp?.by_freq?.Q);
  const [freq, setFreq] = useState("A");
  const grain = freq === "Q" && !hasQ ? "A" : freq;
  return (
    <div className="statrow">
      <div className="statfreq" role="tablist" aria-label={t.grain || "grain"}>
        <button type="button" role="tab" aria-selected={grain === "A"}
                className={`sf ${grain === "A" ? "on" : ""}`} onClick={() => setFreq("A")}>{t.freqYear}</button>
        <span className="sf-sep" aria-hidden="true">⇄</span>
        <button type="button" role="tab" aria-selected={grain === "Q"} disabled={!hasQ}
                title={hasQ ? "" : t.noQuarterly}
                className={`sf ${grain === "Q" ? "on" : ""}`} onClick={() => hasQ && setFreq("Q")}>{t.freqQuarter}</button>
      </div>
      <Stat title={t.exportsLabel} slot={pick(exp, grain)} t={t} lang={lang} />
      <Stat title={t.importsLabel} slot={pick(imp, grain)} t={t} lang={lang} />
      {children}
      {below && <div className="statrow-more">{below}</div>}
    </div>
  );
}
