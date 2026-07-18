"use client";
/**
 * SearchBox.js — everyday-words product search with autocomplete (plan §7.2).
 * @context  The single search box: type Vietnamese/English words, pick a product, the page
 *           re-renders for it. Covered products show a data badge; uncovered show "locked".
 * @limits   Client island (needs keystroke state). Pure UI over lib/catalog; no fetching.
 * @affects  Navigates to /?hs=<code> on the globe, or /country/<code>?hs=<code> when used ON a
 *           country page — so the user can switch product without bouncing back to the globe.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { search } from "../lib/catalog.js";

export default function SearchBox({ lang, placeholder, countryCode }) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  // On phones the box collapses to a round trigger; tapping it slides the input out (CSS-driven, the
  // toggle button + .is-open class only take effect under the mobile breakpoint). Desktop ignores it.
  const [expanded, setExpanded] = useState(false);
  const inputRef = useRef(null);
  const results = useMemo(() => search(q), [q]);

  useEffect(() => { if (expanded) inputRef.current?.focus(); }, [expanded]);

  function pick(hs6) {
    setQ("");
    setOpen(false);
    setExpanded(false);
    // Searching from a country page keeps you on that country — just swaps the product.
    const base = countryCode ? `/country/${countryCode}` : "/";
    router.push(`${base}?hs=${hs6}${lang === "en" ? "&lang=en" : ""}`);
  }

  return (
    <div className={`search ${expanded ? "is-open" : ""}`}>
      <button type="button" className="search-toggle" aria-label={placeholder} aria-expanded={expanded}
              onClick={() => setExpanded((v) => !v)}>
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" aria-hidden>
          <circle cx="8" cy="8" r="6" /><path d="M17 17l-4-4" />
        </svg>
      </button>
      <input
        ref={inputRef}
        className="search-input"
        value={q}
        placeholder={placeholder}
        onChange={(e) => { setQ(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => { setOpen(false); setExpanded(false); }, 150)}
        onKeyDown={(e) => { if (e.key === "Enter" && results[0]) pick(results[0].hs6); }}
        aria-label={placeholder}
      />
      {open && results.length > 0 && (
        <ul className="search-menu">
          {results.map((c) => (
            <li key={c.hs6}>
              <button type="button" className="search-opt" onMouseDown={() => pick(c.hs6)}>
                <span className="search-name">{lang === "en" ? c.name_en : c.name_vi}</span>
                {c.hs6 !== "TOTAL" && <span className="search-hs">HS {c.hs6}</span>}
                <span className={`search-tag ${c.level}`}>
                  {c.level === "category" ? (lang === "en" ? "Category" : "Loại")
                                          : (lang === "en" ? "Product" : "Sản phẩm")}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
