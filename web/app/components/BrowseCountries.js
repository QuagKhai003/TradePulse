"use client";
/**
 * BrowseCountries.js — pill button that opens a searchable country list to drill into (plan §7.3).
 * @context  Alongside the product search: pick a country directly. Filterable; click → country page.
 * @limits   Client island; navigates on select.
 * @affects  Placed next to the search in HeroClient.
 */
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

export default function BrowseCountries({ countries, lang, hs, label }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");

  const list = useMemo(() => {
    const nq = q.trim().toLowerCase();
    const sorted = [...countries].sort((a, b) =>
      (lang === "en" ? a.name_en : a.name_vi).localeCompare(lang === "en" ? b.name_en : b.name_vi));
    return (nq ? sorted.filter((c) => `${c.name_en} ${c.name_vi}`.toLowerCase().includes(nq)) : sorted).slice(0, 80);
  }, [countries, q, lang]);

  function pick(code) {
    setOpen(false);
    router.push(`/country/${code}?hs=${hs}${lang === "en" ? "&lang=en" : ""}`);
  }

  return (
    <div className="browse">
      <button type="button" className="browse-btn" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <span className="browse-globe">◍</span> {label}
      </button>
      {open && (
        <div className="browse-menu">
          <input className="browse-input" autoFocus value={q} onChange={(e) => setQ(e.target.value)}
                 onBlur={() => setTimeout(() => setOpen(false), 160)} placeholder="…" />
          <ul className="scrollx">
            {list.map((c) => (
              <li key={c.code}>
                <button type="button" className="browse-opt" onMouseDown={() => pick(c.code)}>{lang === "en" ? c.name_en : c.name_vi}</button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
