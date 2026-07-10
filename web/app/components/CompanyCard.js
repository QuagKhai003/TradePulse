/**
 * CompanyCard.js — one Layer-2 profile: name + role + country + cited public source (plan §7.4).
 * @context  Shows a public name and a link to the evidence source. NO contact data, ever
 *           (Golden Rule). `locked` blurs paid-tier profiles for the free tier (plan §11).
 * @limits   Presentation only.
 * @affects  Rendered by app/profiles/page.js.
 */
export default function CompanyCard({ c, lang, t, locked }) {
  const roleLabel = c.role === "buyer" ? t.roleBuyer : t.roleSeller;
  return (
    <div className={`company ${locked ? "locked-card" : ""}`}>
      <div className="company-head">
        <span className={`role-tag ${c.role}`}>{roleLabel}</span>
        <span className="company-country muted">{c.country}</span>
      </div>
      <div className="company-name">{c.name}</div>
      <div className="company-src">
        <span className="muted">{t.source}:</span>{" "}
        <a href={c.evidence_url} target="_blank" rel="noopener noreferrer">{c.evidence_source}</a>
      </div>
      <div className="company-verified muted">{t.verified} {c.verified_date}</div>
      {locked && <div className="lockmask">🔒 {t.upgrade}</div>}
    </div>
  );
}
