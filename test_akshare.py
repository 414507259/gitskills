#!/usr/bin/env python3
import akshare as ak
import pandas as pd

print("测试 akshare 数据源...")

# 测试 1: 沪深300成分股
print("\n1. 测试沪深300成分股接口...")
try:
    hs300 = ak.index_stock_cons(symbol="000300")
    print(f"✓ 成功获取 {len(hs300)} 只成分股")
    print(f"  列名: {hs300.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 2: 实时行情
print("\n2. 测试实时行情接口...")
try:
    spot = ak.stock_zh_a_spot()
    print(f"✓ 成功获取 {len(spot)} 只股票")
    print(f"  列名: {spot.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 3: 另一个实时行情接口
print("\n3. 测试东方财富实时行情接口...")
try:
    em_spot = ak.stock_zh_a_spot_em()
    print(f"✓ 成功获取 {len(em_spot)} 只股票")
    print(f"  列名: {em_spot.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 4: 历史行情 (可能更稳定)
print("\n4. 测试历史行情接口...")
try:
    today = pd.Timestamp.now().strftime('%Y%m%d')
    history = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date=today, end_date=today)
    print(f"✓ 成功获取历史数据")
    print(f"  列名: {history.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

print("\n测试完成！")
