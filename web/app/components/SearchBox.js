"use client";
/**
 * SearchBox.js — everyday-words product search with autocomplete (plan §7.2).
 * @context  The single search box: type Vietnamese/English words, pick a product, the page
 *           re-renders for it. Covered products show a data badge; uncovered show "locked".
 * @limits   Client island (needs keystroke state). Pure UI over lib/catalog; no fetching.
 * @affects  Navigates to /?hs=<code> on the globe, or /country/<code>?hs=<code> when used ON a
 *           country page — so the user can switch product without bouncing back to the globe.
 */
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { search } from "../lib/catalog.js";

export default function SearchBox({ lang, placeholder, countryCode }) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const results = useMemo(() => search(q), [q]);

  function pick(hs6) {
    setQ("");
    setOpen(false);
    // Searching from a country page keeps you on that country — just swaps the product.
    const base = countryCode ? `/country/${countryCode}` : "/";
    router.push(`${base}?hs=${hs6}${lang === "en" ? "&lang=en" : ""}`);
  }

  return (
    <div className="search">
      <input
        className="search-input"
        value={q}
        placeholder={placeholder}
        onChange={(e) => { setQ(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
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
