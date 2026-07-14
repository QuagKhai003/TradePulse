import sys
sys.path.insert(0, ".")
from tradepulse_etl.sources.comtrade import ComtradeMirrorSource
from tradepulse_etl.settings import comtrade_key
from tradepulse_etl.transform import transform_all
from tradepulse_etl.db import connect, fill_trade_flows
from tradepulse_etl import config
conn = connect("../data/tradepulse.sqlite")
src = ComtradeMirrorSource(key=comtrade_key())
BATCH = 40
codes = [h for h in config.COVERED_HS if h != "TOTAL"]
total = 0
for i in range(0, len(codes), BATCH):
    chunk = codes[i:i+BATCH]
    raw = src.pull(chunk, [], None)
    rows = transform_all(raw, "comtrade-mirror")
    total += fill_trade_flows(conn, rows)
    print(f"  mirror {i+len(chunk)}/{len(codes)} products, offered {total} rows", flush=True)
print("mirror fill done", flush=True)
