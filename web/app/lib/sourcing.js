/**
 * sourcing.js — load the quarterly partner-sourcing file for a product (plan §7.3).
 * @context  Reads web/public/data/sourcing-<hs>.json (focus reporters only). Returns null if the
 *           product/reporter has no sourcing (the country page then shows annual history instead).
 * @limits   Server-only (fs).
 * @affects  Consumed by app/country/[code]/page.js.
 */
import { readFile } from "node:fs/promises";
import path from "node:path";

export async function loadSourcing(hs) {
  if (!hs) return null;
  const p = path.join(process.cwd(), "public", "data", `sourcing-${hs}.json`);
  try {
    return JSON.parse(await readFile(p, "utf-8"));
  } catch {
    return null;
  }
}
