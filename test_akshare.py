import akshare as ak
import pandas as pd

print("Testing akshare functions...")

# Try different index constituent functions
try:
    print("Trying index_stock_cons_csindex...")
    df = ak.index_stock_cons_csindex(symbol="000300")
    print("Success!")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

try:
    print("\nTrying stock_zh_index_spot_em...")
    df = ak.stock_zh_index_spot_em()
    print("Success!")
    print(df.head())
except Exception as e:
    print(f"Error: {e}")

try:
    print("\nTrying stock_zh_a_spot_em...")
    df = ak.stock_zh_a_spot_em()
    print("Success!")
    print("Columns:", df.columns.tolist())
    print(df[['代码', '名称', '最新价', '涨跌幅']].head())
except Exception as e:
    print(f"Error: {e}")
