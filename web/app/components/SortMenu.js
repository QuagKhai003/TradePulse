"use client";
/**
 * SortMenu.js — compact sort dropdown for the signals feed (plan §7.1).
 * @context  Sort signals by severity (default), % change, value, or name. Client state.
 * @limits   Presentation; onChange lifts to the hero.
 * @affects  Rendered in the signals panel header.
 */
import { useState } from "react";

export default function SortMenu({ value, onChange, t }) {
  const [open, setOpen] = useState(false);
  const opts = [["signal", t.sortSignal], ["change", t.sortChange], ["value", t.sortValue], ["name", t.sortName]];
  const cur = opts.find((o) => o[0] === value) || opts[0];
  return (
    <div className="sortm">
      <button type="button" className="sortm-btn" onClick={() => setOpen((o) => !o)}
              onBlur={() => setTimeout(() => setOpen(false), 160)} aria-expanded={open}>
        <span className="sortm-ic">⇅</span> {cur[1]}
      </button>
      {open && (
        <ul className="sortm-menu">
          {opts.map(([v, l]) => (
            <li key={v}>
              <button type="button" className={`sortm-opt ${v === value ? "on" : ""}`} onMouseDown={() => onChange(v)}>{l}</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
