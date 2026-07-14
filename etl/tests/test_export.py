"""
test_export.py — the web seam: slim snapshot shape + tender display fields.
@context  The snapshot is read by web/app/lib/snapshot.js, which rehydrates the short keys. These
          tests pin the wire format so a change here cannot silently blank the UI.
@limits   Offline; in-memory SQLite.
@affects  tradepulse_etl/export.py
"""
import unittest

from tradepulse_etl.db import connect, upsert_trade_flows
from tradepulse_etl.export import _m49, _subject, build_sellers, build_snapshot


def _row(period, value, flow="X", freq="A", reporter=704):
    return {"reporter": reporter, "partner": 0, "hs6": "0902", "period": period, "freq": freq,
            "flow": flow, "value_usd": value, "quantity": None, "qty_unit": None,
            "source": "comtrade", "published_date": None}


class SlimHistoryTest(unittest.TestCase):
    """History rides a SHARED period index — slots carry values only, so 1,240 files stay small."""

    def test_history_aligned_to_shared_index(self):
        conn = connect(":memory:")
        upsert_trade_flows(conn, [_row("2022", 100.0), _row("2023", 200.0), _row("2024", 300.0)])
        snap = build_snapshot(conn, generated_at="2026-07-14T00:00:00Z", hs6="0902")
        self.assertEqual(snap["periods"]["A"], ["2022", "2023", "2024"])
        self.assertEqual(snap["countries"][0]["e"]["h"], [100, 200, 300])   # no period strings

    def test_gap_in_a_country_series_is_a_hole_not_a_shift(self):
        conn = connect(":memory:")
        upsert_trade_flows(conn, [_row("2022", 100.0), _row("2024", 300.0),      # 2023 missing here
                                  _row("2023", 50.0, reporter=156)])             # but present here
        snap = build_snapshot(conn, generated_at="2026-07-14T00:00:00Z", hs6="0902")
        vn = next(c for c in snap["countries"] if c["c"] == 704)
        self.assertEqual(snap["periods"]["A"], ["2022", "2023", "2024"])
        self.assertEqual(vn["e"]["h"], [100, None, 300])                    # hole, not a slide-left


class TenderDisplayTest(unittest.TestCase):
    """TED titles read 'Country - English subject - LOCAL project name'; we show the English part."""

    def test_subject_is_the_english_segment(self):
        self.assertEqual(_subject("Poland – Vegetables, fruits and nuts – ZP/58 Dostawa warzyw"),
                         "Vegetables, fruits and nuts")

    def test_subject_falls_back_to_whole_title(self):
        self.assertEqual(_subject("Framework for coffee supply"), "Framework for coffee supply")

    def test_buyer_country_maps_to_m49(self):
        self.assertEqual(_m49("POL"), 616)      # so a country page can show its own tenders
        self.assertIsNone(_m49("ZZZ"))


class SellersFromAwardsTest(unittest.TestCase):
    """Sellers are DERIVED from won contracts — a seller is an org that won at least one on-product
    contract. Nothing is inferred beyond that."""

    A = [{"seller": "Scandbio", "seller_country": "LVA", "seller_code": 428, "buyer": "Talsu",
          "date": "2024-11-20", "value": 300.0, "currency": "EUR", "url": "u1"},
         {"seller": "Scandbio", "seller_country": "LVA", "seller_code": 428, "buyer": "Cesu",
          "date": "2025-02-01", "value": 200.0, "currency": "EUR", "url": "u2"},
         {"seller": "EHO", "seller_country": "AUT", "seller_code": 40, "buyer": "OBB",
          "date": "2024-08-29", "value": 100.0, "currency": "EUR", "url": "u3"}]

    def test_ranked_by_wins_and_totalled(self):
        s = build_sellers(self.A)
        self.assertEqual([x["seller"] for x in s], ["Scandbio", "EHO"])
        self.assertEqual(s[0]["wins"], 2)
        self.assertEqual(s[0]["value"], 500.0)
        self.assertEqual(s[0]["last"], "2025-02-01")
        self.assertEqual(s[0]["url"], "u2")            # link points at the most recent win
        self.assertEqual(s[0]["buyers"], ["Talsu", "Cesu"])

    def test_mixed_currencies_give_no_total(self):      # never a number we cannot stand behind
        a = [dict(self.A[0]), dict(self.A[1], currency="USD")]
        self.assertIsNone(build_sellers(a)[0]["value"])


if __name__ == "__main__":
    unittest.main()
