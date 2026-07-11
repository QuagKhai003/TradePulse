"use client";
/**
 * MotionPanel.js — cinematic slide/fade-in wrapper for the overlay panels (framer-motion).
 * @context  Wraps a server panel so it eases in from its side on load; respects reduced motion.
 * @limits   Client island; presentation only.
 * @affects  Wraps TopCountries + GlobalFeed on page.js.
 */
import { motion, useReducedMotion } from "framer-motion";

export default function MotionPanel({ children, className, from = "left", delay = 0 }) {
  const reduce = useReducedMotion();
  const x = reduce ? 0 : from === "right" ? 26 : from === "left" ? -26 : 0;
  const y = reduce ? 0 : from === "top" ? -18 : 0;
  return (
    <motion.aside
      className={className}
      initial={{ opacity: 0, x, y }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ duration: 0.7, ease: [0.22, 0.8, 0.28, 1], delay }}
    >
      {children}
    </motion.aside>
  );
}
