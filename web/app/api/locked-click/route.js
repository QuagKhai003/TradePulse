/**
 * route.js — POST /api/locked-click: record locked-page demand telemetry (plan §7.6).
 * @context  The roadmap oracle: every view/request of an uncovered product is appended as NDJSON.
 *           An ETL step folds this into the locked_page_clicks table in batch 1.8; for now the
 *           raw capture is real and durable so no demand signal is lost.
 * @limits   Append-only NDJSON to ../data/locked_clicks.ndjson (gitignored). Best-effort.
 * @affects  Called by components/LockedProduct.js.
 */
import { appendFile, mkdir } from "node:fs/promises";
import path from "node:path";

const LOG = path.join(process.cwd(), "..", "data", "locked_clicks.ndjson");

export async function POST(request) {
  let body = {};
  try { body = await request.json(); } catch { /* ignore */ }
  const entry = {
    ts: new Date().toISOString(),
    hs6: String(body.hs6 || ""),
    market: body.market ? String(body.market) : null,
    event: body.event === "request" ? "request" : "view",
  };
  try {
    await mkdir(path.dirname(LOG), { recursive: true });
    await appendFile(LOG, JSON.stringify(entry) + "\n", "utf-8");
  } catch {
    return Response.json({ ok: false }, { status: 200 });
  }
  return Response.json({ ok: true });
}
