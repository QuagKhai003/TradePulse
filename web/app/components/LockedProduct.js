"use client";
/**
 * LockedProduct.js — "coming soon — request it" page for uncovered products (plan §7.6).
 * @context  Uncovered verticals are telemetry: the view + the request are logged as demand
 *           evidence for what to build next (the roadmap oracle). No data is faked.
 * @limits   Client island (logs on mount + on request). Posts to /api/locked-click.
 * @affects  Rendered by page.js when the chosen HS is not covered.
 */
import { useEffect, useState } from "react";

export default function LockedProduct({ product, lang }) {
  const [requested, setRequested] = useState(false);
  const name = lang === "en" ? product.name_en : product.name_vi;

  useEffect(() => {
    log({ hs6: product.hs6, event: "view" });
  }, [product.hs6]);

  async function requestIt() {
    await log({ hs6: product.hs6, event: "request" });
    setRequested(true);
  }

  const tx = lang === "en"
    ? { h: `Coverage for ${name} is coming soon.`,
        p: "This product isn't covered yet. Tell us you want it — every request steers what we build next.",
        btn: "Request this product", ok: "Thanks — your request is logged.", hs: "HS code" }
    : { h: `Dữ liệu cho ${name} sắp có.`,
        p: "Sản phẩm này chưa được bao phủ. Hãy cho chúng tôi biết bạn cần — mỗi yêu cầu định hướng thứ chúng tôi làm tiếp theo.",
        btn: "Yêu cầu sản phẩm này", ok: "Cảm ơn — yêu cầu của bạn đã được ghi nhận.", hs: "Mã HS" };

  return (
    <div className="locked">
      <div className="locked-lock">🔒</div>
      <h2 className="locked-h">{tx.h}</h2>
      <p className="locked-p">{tx.p}</p>
      <div className="locked-hs">{tx.hs}: <strong>{product.hs6}</strong></div>
      {requested
        ? <div className="locked-ok">✓ {tx.ok}</div>
        : <button type="button" className="locked-btn" onClick={requestIt}>{tx.btn}</button>}
    </div>
  );
}

async function log(payload) {
  try {
    await fetch("/api/locked-click", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    /* telemetry is best-effort; never block the UI */
  }
}
