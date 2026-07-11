"use client";
/**
 * SortMenu.js — compact sort dropdown for the signals feed (plan §7.1).
 * @context  Sort signals by severity (default), % change, value, or name. The menu is portalled to
 *           <body> with fixed positioning so the panel's overflow:hidden + backdrop-filter (a
 *           containing block) can't clip it. Client state; onChange lifts to the hero.
 * @limits   Presentation; onChange lifts to the hero.
 * @affects  Rendered in the signals panel header.
 */
import { useState, useRef } from "react";
import { createPortal } from "react-dom";

export default function SortMenu({ value, onChange, t }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState(null);
  const btnRef = useRef(null);
  const opts = [["signal", t.sortSignal], ["change", t.sortChange], ["value", t.sortValue], ["name", t.sortName]];
  const cur = opts.find((o) => o[0] === value) || opts[0];

  function toggle() {
    if (!open && btnRef.current) {
      const r = btnRef.current.getBoundingClientRect();
      setPos({ top: r.bottom + 6, right: Math.round(window.innerWidth - r.right) });
    }
    setOpen((o) => !o);
  }

  return (
    <div className="sortm">
      <button ref={btnRef} type="button" className="sortm-btn" onClick={toggle}
              onBlur={() => setTimeout(() => setOpen(false), 160)} aria-expanded={open}>
        <span className="sortm-ic">⇅</span> {cur[1]}
      </button>
      {open && pos && createPortal(
        <ul className="sortm-menu" style={{ position: "fixed", top: pos.top, right: pos.right }}>
          {opts.map(([v, l]) => (
            <li key={v}>
              <button type="button" className={`sortm-opt ${v === value ? "on" : ""}`}
                      onMouseDown={() => { onChange(v); setOpen(false); }}>{l}</button>
            </li>
          ))}
        </ul>,
        document.body,
      )}
    </div>
  );
}
