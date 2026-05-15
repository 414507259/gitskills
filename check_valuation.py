#!/usr/bin/env python3
import akshare as ak
import pandas as pd

print("查看估值数据...")

# 测试百度估值接口
try:
    # 获取多个股票的估值
    for symbol in ['600519', '000001', '601398']:
        print(f"\n股票: {symbol}")
        val = ak.stock_zh_valuation_baidu(symbol=symbol)
        print(val.head())
        print(f"列名: {val.columns.tolist()}")
except Exception as e:
    print(f"失败: {e}")

# 测试其他可能的接口
print("\n\n尝试其他可能的数据源...")
try:
    # 尝试获取行情数据
    from akshare import stock_zh_a_spot
    spot = stock_zh_a_spot()
    print(f"\n实时行情数据样本:")
    print(spot[['代码', '名称', '最新价', '涨跌幅']].head(10))
    print(f"\n总共有 {len(spot)} 只股票")
except Exception as e:
    print(f"实时行情获取失败: {e}")

# 尝试获取指数数据
print("\n\n尝试获取指数数据...")
try:
    index_data = ak.index_zh_a_hist(symbol="000300", period="daily")
    print(f"指数数据成功获取")
    print(index_data.tail())
except Exception as e:
    print(f"指数数据失败: {e}")
