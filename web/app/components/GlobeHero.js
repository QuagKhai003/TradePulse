"use client";
/**
 * GlobeHero.js — client wrapper for the 3D globe (dynamic ssr:false) + a cinematic intro.
 * @context  Loads GlobeInner only in the browser (three.js/window). framer-motion fades + scales
 *           the globe in on mount for a premium reveal.
 * @limits   Client island. All heavy WebGL lives in GlobeInner.
 * @affects  Placed in the hero on page.js.
 */
import dynamic from "next/dynamic";
import { motion } from "framer-motion";

const GlobeInner = dynamic(() => import("./GlobeInner.js"), {
  ssr: false,
  loading: () => <div className="globe-loading" aria-hidden />,
});

export default function GlobeHero(props) {
  return (
    <motion.div
      className="globe-mount"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 1.2, ease: [0.22, 0.8, 0.28, 1] }}
    >
      <GlobeInner {...props} />
    </motion.div>
  );
}
