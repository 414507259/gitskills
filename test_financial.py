#!/usr/bin/env python3
import akshare as ak
import pandas as pd

print("测试财务数据接口...")

# 测试 1: 个股财务指标
print("\n1. 测试个股财务指标接口...")
try:
    # 获取个股财务指标
    fin = ak.stock_individual_spot_xq(symbol="SH600519")
    print(f"✓ 成功获取财务数据")
    print(f"  数据: {fin}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 2: 股票列表 - 可能包含更多信息
print("\n2. 测试股票列表接口...")
try:
    stock_list = ak.stock_info_a_code_name()
    print(f"✓ 成功获取 {len(stock_list)} 只股票")
    print(f"  列名: {stock_list.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 3: 指数成分股信息
print("\n3. 测试指数成分股信息...")
try:
    # 沪深300
    hs300 = ak.index_stock_cons_sina(symbol="sh000300")
    print(f"✓ 成功获取 {len(hs300)} 只成分股")
    print(f"  列名: {hs300.columns.tolist()}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试 4: 尝试其他可能的接口
print("\n4. 测试其他数据源...")
interfaces_to_try = [
    ('stock_individual_info_em', 'ak.stock_individual_info_em(symbol="600519")'),
    ('stock_zh_valuation_baidu', 'ak.stock_zh_valuation_baidu(symbol="600519")'),
]

for name, code in interfaces_to_try:
    print(f"\n   尝试 {name}...")
    try:
        result = eval(code)
        print(f"   ✓ 成功! 列名: {result.columns.tolist() if hasattr(result, 'columns') else str(type(result))}")
    except Exception as e:
        print(f"   ✗ 失败: {e}")

print("\n测试完成!")
