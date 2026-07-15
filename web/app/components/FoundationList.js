/**
 * FoundationList.js — the qualification tab's FOUNDATION informed-list.
 * @context  Baseline things to KNOW before shipping this product to this market (invoice, origin, phyto/
 *           health certs, destination limits). An informed list, NOT a checklist and NOT a guarantee —
 *           framed as general guidance, each item linking to the official portal that confirms specifics.
 * @limits   Presentational. Shown only when a verified market portal + a product category exist (loader
 *           returns null otherwise). Golden Rule: every item carries an official source + verified date.
 * @affects  Rendered by QualPanel. Data from lib/foundation.js (content/requirements/foundation.json).
 */
export default function FoundationList({ foundation, lang, t }) {
  if (!foundation || !foundation.items.length) return null;
  const framing = lang === "en" ? foundation.framing_en : foundation.framing_vi;
  return (
    <div className="fnd">
      <h3 className="fnd-h">{t.fndTitle} <span className="fnd-tag muted small">{t.fndTag}</span></h3>
      <p className="muted small fnd-note">{framing}</p>
      <ul className="fnd-list">
        {foundation.items.map((it) => (
          <li key={it.id} className="fnd-item">
            <span className="fnd-label">{lang === "en" ? it.label_en : it.label_vi}</span>
            <span className="muted small fnd-desc">{lang === "en" ? it.note_en : it.note_vi}</span>
            <a className="fnd-src small" href={it.source.url} target="_blank" rel="noopener noreferrer">
              {it.source.portal} ↗ · {it.source.verified}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
