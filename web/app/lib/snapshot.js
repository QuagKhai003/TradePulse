/**
 * snapshot.js — load the ETL-generated Layer-1 snapshot (the web/ETL seam).
 * @context  Reads web/public/data/snapshot.json at request time so re-running the ETL shows up
 *           without a rebuild. Returns null if it is missing (page then tells the user to run ETL).
 * @limits   Server-only (uses node:fs). Never bundle the DB — this file is the whole contract.
 * @affects  Consumed by app/page.js. Contract documented in docs/DATA_MODEL.md.
 */
import { readFile } from "node:fs/promises";
import path from "node:path";

export async function loadSnapshot() {
  const p = path.join(process.cwd(), "public", "data", "snapshot.json");
  try {
    return JSON.parse(await readFile(p, "utf-8"));
  } catch {
    return null;
  }
}
