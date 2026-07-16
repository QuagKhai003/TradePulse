/**
 * QualPanel.js — market-entry qualifications for a product×country (plan §7.5, Layer 3 entry point).
 * @context  On a country drill, shows what it takes to bring the product INTO that market (the
 *           exporter's gate). Covered pairs (pellets→JP/KR/EU) show the snapshot + a sourced teaser
 *           + a link to the full checklist; uncovered pairs show "request it" (demand telemetry §7.6).
 * @limits   Inform-never-match; every shown item is source-backed (loader drops unsourced).
 * @affects  Rendered by country/[code]/page.js. Reads lib/requirements.
 */
import Link from "next/link";
import RequestQual from "./RequestQual.js";
import FoundationList from "./FoundationList.js";
import { loadRequirement } from "../lib/requirements.js";
import { MARKET_SLUG } from "../lib/events.js";
import { loadFoundation } from "../lib/foundation.js";

const REQ_MARKET = { 392: "jp", 410: "kr", 97: "eu" };
const MANDATORY = { "yes": "req-yes", "de-facto": "req-def", "phasing-in": "req-phase" };

// Just the FOUNDATION (baseline things to know) + the full-checklist request. Regulatory news is now
// its OWN section on the page, not nested here.
export default async function QualPanel({ hs, code, product, country, lang, t }) {
  const slug = hs === "440131" ? REQ_MARKET[code] : null;
  const d = slug ? await loadRequirement(slug) : null;
  const qs = lang === "en" ? "?lang=en" : "";
  const mktSlug = MARKET_SLUG[Number(code)] || null;

  if (!d) {
    const foundation = await loadFoundation(hs, mktSlug);
    // Show the baseline foundation where we have it; only fall back to the "request it" prompt (the lock)
    // when there is no foundation for this product×market — so a covered pair never shows a stray lock.
    return (
      <section className="panel qual">
        {foundation
          ? <FoundationList foundation={foundation} lang={lang} t={t} />
          : <RequestQual hs={hs} market={String(code)} product={product} country={country} lang={lang} />}
      </section>
    );
  }

  const snapshot = lang === "en" ? d.snapshot_en : d.snapshot_vi;
  const items = d.requirements.slice(0, 3);
  return (
    <section className="panel qual">
      <h2>{t.qualTitle} <span className="muted">· {product} → {country}</span></h2>
      <p className="muted small">{t.qualEnter} · {t.lastReview}: {d.last_full_review}</p>
      <p>{snapshot}</p>
      <ul className="qual-list">
        {items.map((r) => (
          <li key={r.seq}>
            <span className={`req-badge ${MANDATORY[r.mandatory] || "req-def"}`}>{r.mandatory}</span>
            <span className="qual-text">{lang === "en" ? r.text_en : r.text_vi}</span>
            <a href={r.source_url} target="_blank" rel="noopener noreferrer">{r.source}</a>
            <span className="muted small"> · {r.verified_date}</span>
          </li>
        ))}
      </ul>
      <Link className="chip link" href={`/requirements/${slug}${qs}`}>{t.qualViewFull}</Link>
    </section>
  );
}
