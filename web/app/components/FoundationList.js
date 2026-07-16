/**
 * FoundationList.js — the "Minimum qualification entry" informed-list.
 * @context  Baseline things to KNOW before shipping this product to this market (invoice, origin, phyto/
 *           health certs, destination limits). NOT a checklist and NOT a guarantee — general guidance,
 *           each item linking to the official portal that confirms specifics. Laid out as a clean grid
 *           of items (no divider-per-row), so it reads at a glance.
 * @limits   Presentational. Shown only when a verified market portal + a product category exist.
 *           Golden Rule: every item carries an official source + verified date.
 * @affects  Rendered by QualPanel. Data from lib/foundation.js (content/requirements/foundation.json).
 */
export default function FoundationList({ foundation, lang, t }) {
  if (!foundation || !foundation.items.length) return null;
  return (
    <div className="fnd">
      <div className="fnd-grid">
        {foundation.items.map((it) => (
          <div key={it.id} className="fnd-item">
            <div className="fnd-label">{lang === "en" ? it.label_en : it.label_vi}</div>
            <div className="fnd-desc muted small">{lang === "en" ? it.note_en : it.note_vi}</div>
            <a className="fnd-src small" href={it.source.url} target="_blank" rel="noopener noreferrer">
              {it.source.portal} ↗ <span className="muted">· {it.source.verified}</span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
