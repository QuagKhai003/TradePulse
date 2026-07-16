"use client";
/**
 * MarketFeed.js — the parties behind a product in one market: buyers, sellers, past orders.
 * @context  Master–detail. Left: a tab rail + compact scannable rows, each one organisation. Right: the
 *           full public record for the row you picked, held in view while you keep scanning the list —
 *           a modal would hide the list every time you compared two companies, and comparing is the job.
 * @warn     The three tabs ALWAYS render, for every product and country. The layout is a constant; only
 *           its contents change. An empty tab says WHY it is empty (no coverage / nothing on record /
 *           aggregate heading) instead of vanishing — a disappearing tab reads as "nothing exists" when
 *           it means "we have no coverage here", and those are very different facts to a factory owner.
 * @golden   Inform, never match. Every row is an ORGANISATION plus the public notice that evidences it.
 *           Never a contact person, an email or a phone — TED publishes those; we do not carry them.
 * @limits   Presentation + tab/selection state. The paywall (locked rows) is decided SERVER-side and
 *           passed in as openCount: a locked row blurs the WHOLE row (owner's call) and cannot be
 *           selected — it links to /pricing instead. The count stays visible, so the tab still tells
 *           the truth about how much is there.
 * @affects  Rendered by country/[code]/page.js. Rows built from lib/tenders (tenders, sellers, awards).
 */
import { useState } from "react";
import Link from "next/link";
import { fmtDeadline, fmtMoney } from "../lib/format.js";
import { lookup } from "../lib/catalog.js";

const CAP = 60;   // rows rendered; the rollup holds thousands and the rest are locked teasers anyway

const productName = (hs) => (hs ? (lookup(hs)?.name_en || `HS ${hs}`) : "");

export default function MarketFeed({ tenders = [], sellers = [], orders = [], product, country,
                                     cpv, hs, lang, t, openCount = Infinity }) {
  const [tab, setTab] = useState("buyers");
  const [pick, setPick] = useState(0);
  const [page, setPage] = useState(0);
  const PER = 8;

  // "All products" is not a good anyone tenders for — but the answer it owes is real: everything,
  // across every product. So it is a rollup, and each row names the product it belongs to.
  const isAggregate = hs === "TOTAL" || cpv?.aggregate;
  const noCoverage = !isAggregate && !cpv;

  const items = { buyers: tenders, sellers, orders }[tab] || [];
  const rows = items.slice(0, CAP).map((x, i) => toRow(tab, x, i >= openCount, isAggregate, lang, t));
  const chosen = rows[Math.min(pick, rows.length - 1)];
  const pageCount = Math.max(1, Math.ceil(rows.length / PER));
  // Pad the last (short) page up to a full PER slots so the list box keeps ONE height on every page —
  // otherwise 8 real rows are a hair taller than the min-height and the short page visibly collapses.
  const onPage = Math.min(PER, Math.max(0, rows.length - page * PER));
  const fillerCount = pageCount > 1 ? PER - onPage : 0;

  const tabs = [
    { v: "buyers", label: t.tabBuyers, n: tenders.length },
    { v: "sellers", label: t.tabSellers, n: sellers.length },
    { v: "orders", label: t.tabOrders, n: orders.length },
  ];

  function choose(v) {
    setTab(v);
    setPick(0);
    setPage(0);
  }

  return (
    <section className="mfeed">
      <header className="mfeed-head">
        <div className="mfeed-tabs">
          {tabs.map((x) => (
            <button key={x.v} type="button" className={`ctab ${tab === x.v ? "on" : ""}`}
                    onClick={() => choose(x.v)}>
              {x.label} <b className="num">{x.n}</b>
            </button>
          ))}
        </div>
      </header>

      {noCoverage ? (
        <p className="mfeed-empty muted">{t.noCpvNote}</p>
      ) : rows.length === 0 ? (
        <p className="mfeed-empty muted">{emptyLine(tab, product, country, t)}</p>
      ) : (
        <div className="mfeed-body">
          <div className="mfeed-list">
            <ul>
              {rows.map((r, i) => (i < page * PER || i >= (page + 1) * PER) ? null : (
                <li key={r.key}>
                  {r.locked ? (
                    // Locked: the whole row blurs and cannot be selected — it goes to /pricing. The tab
                    // COUNT still shows the real total, so the paywall hides the rows, never the truth
                    // about how many there are.
                    <Link className="mrow locked" href="/pricing">
                      <span className="mrow-num">{i + 1}</span>
                      <span className="mrow-blur">
                        <span className="mrow-name">{r.name}</span>
                        <span className="mrow-meta">
                          <span className="mrow-cty">{r.country}</span>
                          <span className="mrow-fact">{r.rowFact}</span>
                        </span>
                      </span>
                      <span className="mrow-lock">🔒 {t.upgrade}</span>
                    </Link>
                  ) : (
                    <button type="button" className={`mrow ${i === Math.min(pick, rows.length - 1) ? "on" : ""}`}
                            onClick={() => setPick(i)}>
                      <span className="mrow-num">{i + 1}</span>
                      <span className="mrow-name">{r.name}</span>
                      <span className="mrow-meta">
                        {/* a "One lot" chip so a food-framework contract with a coffee lot never reads
                            as a mismatch — the buyer bundled it, and this row is the relevant lot */}
                        {r.lot != null && <span className={`kind ${r.lot ? "lot" : "contract"}`}>{r.lot ? t.matchLot : t.matchContract}</span>}
                        <span className="mrow-cty">{r.country}</span>
                        <span className="mrow-fact">{r.rowFact}</span>
                      </span>
                    </button>
                  )}
                </li>
              ))}
              {/* keep the last (short) page the exact height of a full one — no visible shrink */}
              {Array.from({ length: fillerCount }).map((_, k) => (
                <li key={`fill-${k}`} className="mrow-fill" aria-hidden="true"><span className="mrow">&nbsp;</span></li>
              ))}
            </ul>
            {pageCount > 1 && (
              <nav className="mfeed-pager">
                <button type="button" disabled={page === 0} onClick={() => setPage(page - 1)} aria-label="Previous">‹</button>
                <span className="mfeed-page">{page + 1} / {pageCount}</span>
                <button type="button" disabled={page >= pageCount - 1} onClick={() => setPage(page + 1)} aria-label="Next">›</button>
              </nav>
            )}
          </div>

          <aside className="mfeed-detail">
            {chosen && !chosen.locked ? (
              <>
                <div className="mdet-tags">
                  <span className={`tender-kind ${chosen.tagKind}`}>{chosen.tag}</span>
                  <span className="flowtag import">{chosen.country}</span>
                </div>
                <h3 className="mdet-name">{chosen.name}</h3>
                <dl className="modal-dl">
                  {chosen.facts.map(([k, v]) => (
                    <div key={k} className="mdet-row"><dt>{k}</dt><dd>{v}</dd></div>
                  ))}
                </dl>
                {/* Golden Rule: the public record is the only thing we hand over. */}
                <p className="modal-note muted">{chosen.note}</p>
                <a className="modal-cta" href={chosen.url} target="_blank" rel="noopener noreferrer">
                  {chosen.cta} ↗
                </a>
              </>
            ) : (
              <p className="muted mdet-empty">{t.pickOne}</p>
            )}
          </aside>
        </div>
      )}
    </section>
  );
}

function emptyLine(tab, product, country, t) {
  if (tab === "buyers") return t.emptyBuyers;
  if (tab === "sellers") return t.emptySellers;
  return t.emptyOrders;
}

// One shape for all three tabs: an organisation + the record that proves it.
function toRow(tab, x, locked, isAggregate, lang, t) {
  const prod = isAggregate ? productName(x.hs6) : null;

  if (tab === "buyers") {
    const due = fmtDeadline(x.deadline, lang);
    const isLot = x.match === "lot";
    return {
      key: x.id, locked, name: x.buyer || x.title, country: x.buyer_country, lot: isLot,
      rowFact: due.label, tag: prod || (isLot ? t.matchLot : t.matchContract),
      tagKind: isLot ? "lot" : "contract",
      facts: [[t.mProduct, prod || t.product], [t.mContract, x.title],
              [t.mDeadline, x.deadline || t.mNoDeadline], [t.mPublished, x.published || "—"],
              [t.mCpv, x.cpv], [t.mNotice, x.id]],
      note: isLot ? t.mLotNote : t.mContractNote, url: x.url, cta: t.mOpenTed,
    };
  }

  if (tab === "sellers") {
    // A registry seller = a company APPROVED to export this product (not a contract winner).
    return {
      key: `${x.seller}-${x.seller_code}`, locked, name: x.seller, country: x.seller_country,
      rowFact: x.approval_no || x.activity || "",
      tag: t.roleSeller, tagKind: "contract",
      facts: [[t.sApproval, x.approval_no || "—"], [t.sActivity, x.activity || "—"],
              [t.sCity, x.city || "—"], [t.sVerified, x.verified || "—"]],
      note: t.sellerNote, url: x.url, cta: t.sOpenRegistry,
    };
  }

  return {
    key: `${x.id}-${x.seller}`, locked, name: x.seller, country: `${x.seller_country} → ${x.buyer_country}`,
    lot: x.match === "lot",
    rowFact: x.value ? fmtMoney(x.value, x.currency) : (x.date || ""),
    tag: prod || (x.match === "lot" ? t.matchLot : t.matchContract),
    tagKind: x.match === "lot" ? "lot" : "contract",
    facts: [[t.mProduct, prod || t.product], [t.roleSeller, `${x.seller} (${x.seller_country})`],
            [t.roleBuyer, `${x.buyer} (${x.buyer_country})`],
            [t.orderValue, x.value ? fmtMoney(x.value, x.currency) : t.sellerNoValue],
            [t.orderDate, x.date || "—"], [t.mContract, x.title], [t.mCpv, x.cpv]],
    note: t.orderNote, url: x.url, cta: t.mOpenTed,
  };
}
