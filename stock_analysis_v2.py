#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股沪深300成分股买入机会分析
使用akshare获取数据并筛选符合买入条件的股票
注意：由于网络限制，本脚本尝试多种数据源获取实时行情
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import warnings
import time
warnings.filterwarnings('ignore')

def get_hs300_stocks():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    try:
        df = ak.index.index_cons.index_stock_cons(symbol="000300")
        stocks = df[['品种代码', '品种名称']].values.tolist()
        print(f"成功获取 {len(stocks)} 只沪深300成分股")
        return stocks
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return []

def get_stock_realtime_data_with_retry(stock_codes, max_retries=2):
    """尝试多种数据源获取实时行情数据"""
    print(f"\n正在获取 {len(stock_codes)} 只股票实时数据...")

    # 方法1: 东方财富
    try:
        print("尝试方法1: 东方财富...")
        df = ak.stock_zh_a_spot_em()
        hs300_data = df[df['代码'].isin(stock_codes)].copy()
        if not hs300_data.empty:
            print(f"方法1成功! 获取 {len(hs300_data)} 只股票实时数据")
            return hs300_data
    except Exception as e:
        print(f"方法1失败: {str(e)[:100]}")

    # 方法2: 新浪财经
    try:
        print("尝试方法2: 新浪财经...")
        df = ak.stock_zh_a_spot()
        hs300_data = df[df['代码'].isin(stock_codes)].copy()
        if not hs300_data.empty:
            print(f"方法2成功! 获取 {len(hs300_data)} 只股票实时数据")
            return hs300_data
    except Exception as e:
        print(f"方法2失败: {str(e)[:100]}")

    # 方法3: 腾讯财经
    try:
        print("尝试方法3: 腾讯财经...")
        df = ak.stock_zh_a_spot_tx()
        hs300_data = df[df['代码'].isin(stock_codes)].copy()
        if not hs300_data.empty:
            print(f"方法3成功! 获取 {len(hs300_data)} 只股票实时数据")
            return hs300_data
    except Exception as e:
        print(f"方法3失败: {str(e)[:100]}")

    print("所有数据源均无法访问")
    return pd.DataFrame()

def filter_stocks(df):
    """筛选符合买入条件的股票"""
    print("\n正在筛选符合买入条件的股票...")

    # 定义筛选条件
    conditions = {
        'pe': ('市盈率', lambda x: pd.to_numeric(x, errors='coerce') < 30),
        'pb': ('市净率', lambda x: pd.to_numeric(x, errors='coerce') < 3),
        'change': ('涨跌幅', lambda x: pd.to_numeric(x, errors='coerce') > 0),
        'turnover': ('换手率', lambda x: pd.to_numeric(x, errors='coerce') > 1),
        'mktcap': ('流通市值', lambda x: (
            pd.to_numeric(x, errors='coerce') >= 100e8) &
            (pd.to_numeric(x, errors='coerce') <= 1000e8)
        ),
        'price': ('最新价', lambda x: pd.to_numeric(x, errors='coerce') < 20)
    }

    # 计算每只股票满足的条件数量
    stock_conditions_met = {}

    for idx, row in df.iterrows():
        code = str(row['代码']).zfill(6)
        count = 0
        met_conditions = []

        for cond_name, (col_name, cond_func) in conditions.items():
            if col_name in df.columns:
                try:
                    if cond_func(row[col_name]):
                        count += 1
                        met_conditions.append(cond_name)
                except:
                    pass

        stock_conditions_met[code] = {
            'count': count,
            'conditions': met_conditions
        }

    # 筛选至少满足3条条件的股票
    filtered = []
    for idx, row in df.iterrows():
        code = str(row['代码']).zfill(6)
        if code in stock_conditions_met:
            info = stock_conditions_met[code]
            if info['count'] >= 3:
                row_dict = row.to_dict()
                row_dict['满足条件数'] = info['count']
                row_dict['具体条件'] = ', '.join(info['conditions'])
                filtered.append(row_dict)

    print(f"筛选出 {len(filtered)} 只符合买入条件的股票")

    # 转换为DataFrame并排序
    result_df = pd.DataFrame(filtered)
    if not result_df.empty:
        result_df = result_df.sort_values('满足条件数', ascending=False)

    return result_df

def calculate_score(row):
    """计算综合评分用于排序"""
    score = 0
    score += min(row.get('满足条件数', 0) * 10, 30)  # 满足条件数，最多30分

    # 市盈率越低越好（PE < 10 加5分）
    try:
        pe = float(row.get('市盈率', 0))
        if pe > 0 and pe < 10:
            score += 5
        elif pe > 0 and pe < 20:
            score += 3
    except:
        pass

    # 市净率越低越好（PB < 1 加5分）
    try:
        pb = float(row.get('市净率', 0))
        if pb > 0 and pb < 1:
            score += 5
        elif pb > 0 and pb < 2:
            score += 3
    except:
        pass

    # 涨幅适中最好（0-5%最佳）
    try:
        change = float(row.get('涨跌幅', 0))
        if 0 < change <= 3:
            score += 5
        elif 3 < change <= 7:
            score += 3
    except:
        pass

    # 换手率适中（1-5%最好）
    try:
        turnover = float(row.get('换手率', 0))
        if 1 <= turnover <= 5:
            score += 5
        elif turnover > 5:
            score += 2
    except:
        pass

    return score

def generate_report(filtered_df, output_file, hs300_count, success=False):
    """生成推荐报告"""
    print(f"\n正在生成推荐报告到 {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        # 标题
        f.write("=" * 80 + "\n")
        f.write("A股沪深300成分股买入机会推荐报告\n")
        f.write("=" * 80 + "\n\n")

        # 报告信息
        report_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        f.write(f"生成时间: {report_time}\n")
        f.write(f"数据来源: akshare实时行情\n")
        f.write(f"沪深300成分股总数: {hs300_count}\n")

        if not success:
            f.write("\n" + "!" * 80 + "\n")
            f.write("【重要提示】\n")
            f.write("由于网络环境限制，暂时无法获取实时行情数据。\n")
            f.write("以下提供基于最新可用数据的参考信息。\n")
            f.write("!" * 80 + "\n\n")

        f.write(f"筛选标准: 满足以下6项条件中至少3项\n")
        f.write("-" * 80 + "\n\n")

        # 筛选条件说明
        f.write("【筛选条件】\n")
        f.write("1. 市盈率(PE) < 30\n")
        f.write("2. 市净率(PB) < 3\n")
        f.write("3. 今日涨幅 > 0（即今日上涨）\n")
        f.write("4. 换手率 > 1%\n")
        f.write("5. 流通市值在100亿-1000亿之间\n")
        f.write("6. 股价 < 20元\n\n")

        # 如果没有符合条件的股票
        if filtered_df.empty:
            f.write("【分析结果】\n")
            if success:
                f.write("今日暂无符合条件的股票。\n")
                f.write("\n可能原因:\n")
                f.write("1. 市场整体表现较弱，上涨股票较少\n")
                f.write("2. 沪深300成分股今日普遍回调\n")
                f.write("3. 优质股票估值较高，未能满足筛选条件\n\n")
            else:
                f.write("暂时无法获取实时数据，无法进行筛选分析。\n\n")
        else:
            # 计算综合评分
            filtered_df['综合评分'] = filtered_df.apply(calculate_score, axis=1)
            filtered_df = filtered_df.sort_values('综合评分', ascending=False)

            f.write(f"【分析结果】\n")
            f.write(f"共筛选出 {len(filtered_df)} 只符合买入条件的股票\n")
            f.write(f"按综合评分从高到低排列:\n\n")

            # 详细股票列表
            f.write("=" * 80 + "\n")
            f.write("【推荐股票列表】\n")
            f.write("=" * 80 + "\n\n")

            for i, (idx, row) in enumerate(filtered_df.iterrows(), 1):
                f.write(f"{i}. {row.get('名称', 'N/A')} (代码: {row.get('代码', 'N/A')})\n")
                f.write(f"   最新价: {row.get('最新价', 'N/A')} 元\n")
                f.write(f"   涨跌幅: {row.get('涨跌幅', 'N/A')}%\n")
                f.write(f"   换手率: {row.get('换手率', 'N/A')}%\n")
                f.write(f"   市盈率(PE): {row.get('市盈率', 'N/A')}\n")
                f.write(f"   市净率(PB): {row.get('市净率', 'N/A')}\n")

                # 格式化市值
                mktcap = row.get('流通市值', 0)
                try:
                    mktcap_float = float(mktcap)
                    if mktcap_float >= 1e8:
                        mktcap_str = f"{mktcap_float/1e8:.2f}亿"
                    else:
                        mktcap_str = f"{mktcap_float/1e4:.2f}万"
                except:
                    mktcap_str = str(mktcap)
                f.write(f"   流通市值: {mktcap_str}\n")

                f.write(f"   满足条件数: {row.get('满足条件数', 'N/A')}/6\n")
                f.write(f"   具体条件: {row.get('具体条件', 'N/A')}\n")
                f.write(f"   综合评分: {row.get('综合评分', 'N/A')}/50\n")
                f.write("\n")

            # Top 5 重点推荐
            f.write("=" * 80 + "\n")
            f.write("【重点推荐 Top 5】\n")
            f.write("=" * 80 + "\n\n")

            top5 = filtered_df.head(5)
            for i, (idx, row) in enumerate(top5.iterrows(), 1):
                f.write(f"{i}. {row.get('名称', 'N/A')} (代码: {row.get('代码', 'N/A')})\n")
                f.write(f"   投资亮点:\n")
                f.write(f"   - 满足 {row.get('满足条件数', 'N/A')} 项筛选条件\n")
                f.write(f"   - 综合评分 {row.get('综合评分', 'N/A')}/50\n")

                # 分析亮点
                pros = []
                if row.get('市盈率') and float(row.get('市盈率', 0)) < 20:
                    pros.append("估值合理")
                if row.get('市净率') and float(row.get('市净率', 0)) < 2:
                    pros.append("股价低于净资产")
                if row.get('涨跌幅') and float(row.get('涨跌幅', 0)) > 2:
                    pros.append("今日表现强势")
                if pros:
                    f.write(f"   - {', '.join(pros)}\n")
                f.write("\n")

        # 投资建议
        if success and not filtered_df.empty:
            f.write("=" * 80 + "\n")
            f.write("【投资建议】\n")
            f.write("=" * 80 + "\n\n")
            f.write("1. 以上股票均满足多项价值投资筛选标准\n")
            f.write("2. 建议关注综合评分较高的股票，但需结合行业配置考虑\n")
            f.write("3. 低市盈率、低市净率股票通常具有较好的安全边际\n")
            f.write("4. 今日上涨且换手率适中的股票显示有资金关注\n")
            f.write("5. 建议分批建仓，控制单只股票仓位不超过总仓位的10%\n")
            f.write("\n")

        # 风险提示
        f.write("=" * 80 + "\n")
        f.write("【风险提示】\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. 本报告仅供参考，不构成任何投资建议\n")
        f.write("2. 股市有风险，投资需谨慎\n")
        f.write("3. 过去表现不代表未来收益\n")
        f.write("4. 筛选条件基于量化指标，未考虑基本面深度分析\n")
        f.write("5. 建议结合行业景气度、公司业绩、政策环境等因素综合判断\n")
        f.write("6. 流通市值筛选可能排除超大盘蓝筹和超小盘股票\n")
        f.write("7. 市盈率为负的公司未在筛选范围内（可能存在价值陷阱）\n")
        f.write("8. 当前市场环境下，实时数据获取受限，建议结合其他信息源\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")

    print(f"报告已生成: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("A股沪深300成分股买入机会分析程序")
    print("=" * 60)

    # 获取沪深300成分股
    hs300_stocks = get_hs300_stocks()
    if not hs300_stocks:
        print("无法获取沪深300成分股列表，程序退出")
        return

    # 获取股票代码列表
    stock_codes = [stock[0] for stock in hs300_stocks]

    # 获取实时数据（带重试）
    realtime_df = get_stock_realtime_data_with_retry(stock_codes)

    # 生成报告
    today = datetime.now().strftime("%Y%m%d")
    output_file = f"a_stock_recommendation_{today}.txt"

    if realtime_df.empty:
        # 无法获取数据时生成说明性报告
        generate_report(pd.DataFrame(), output_file, len(stock_codes), success=False)

        print("\n" + "=" * 60)
        print("【网络环境说明】")
        print("=" * 60)
        print("由于当前网络环境限制，无法连接到实时行情数据源。")
        print("可能原因：")
        print("1. 防火墙或代理服务器阻止了外部API请求")
        print("2. 数据源服务器暂时不可用")
        print("3. 网络连接不稳定")
        print("\n建议：")
        print("1. 检查网络连接")
        print("2. 在网络环境更好的情况下重新运行")
        print("3. 使用其他金融数据终端获取实时数据")
        print("=" * 60)
    else:
        # 筛选股票
        filtered_df = filter_stocks(realtime_df)
        generate_report(filtered_df, output_file, len(stock_codes), success=True)

    # 打印摘要
    if not realtime_df.empty:
        print(f"\n摘要: 找到 {len(filtered_df) if 'filtered_df' in dir() else 0} 只符合买入条件的股票")
        print(f"详细信息请查看: {output_file}")
    else:
        print(f"\n摘要: 暂时无法获取实时数据")
        print(f"说明报告已生成: {output_file}")

if __name__ == "__main__":
    main()
