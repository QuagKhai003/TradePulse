/**
 * next.config.mjs — TradePulse web config.
 * @context  Minimal. JSON imports (world-atlas topojson) work out of the box.
 * @limits   Keep small; no experimental flags unless a batch needs one.
 */
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
