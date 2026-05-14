#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import pandas as pd
from datetime import datetime
import warnings
import time
import os
warnings.filterwarnings('ignore')
os.environ['NO_PROXY'] = 'eastmoney.com, Sina.com'

def get_hs300_stocks():
    """获取沪深300成分股列表"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print("正在获取沪深300成分股列表...")
            hs300 = ak.index_stock_cons(symbol="000300")
            print(f"获取成功，共 {len(hs300)} 只成分股")
            return hs300
        except Exception as e:
            print(f"获取沪深300成分股失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

def get_realtime_quotes(stock_list):
    """获取个股实时行情数据 - 尝试多个数据源"""
    data_sources = [
        ("东方财富", lambda: ak.stock_zh_a_spot_em()),
        ("新浪财经", lambda: ak.stock_zh_a_spot()),
        ("腾讯证券", lambda: ak.stock_zh_a_spot_tx()),
    ]
    
    for source_name, data_func in data_sources:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"正在从{source_name}获取实时行情数据 (尝试 {attempt + 1}/{max_retries})...")
                quotes = data_func()
                print(f"从{source_name}获取成功，共 {len(quotes)} 只股票行情")
                return quotes
            except Exception as e:
                print(f"从{source_name}获取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
    
    print("所有数据源均失败，尝试批量获取...")
    return get_batch_stock_data(stock_list)

def get_batch_stock_data(stock_list):
    """批量获取股票数据作为备选方案"""
    print(f"尝试批量获取 {len(stock_list)} 只股票的数据...")
    try:
        batch_data = []
        stock_codes = stock_list['品种代码'].tolist()[:50]
        
        for i, code in enumerate(stock_codes):
            try:
                if i % 10 == 0:
                    print(f"正在获取第 {i+1}-{min(i+10, len(stock_codes))} 只股票...")
                stock_info = ak.stock_individual_info_em(symbol=code)
                batch_data.append(stock_info)
                time.sleep(0.5)
            except Exception as e:
                continue
        
        if batch_data:
            combined_df = pd.concat(batch_data, ignore_index=True)
            return combined_df
    except Exception as e:
        print(f"批量获取也失败: {e}")
    
    return None

def filter_stocks(hs300_df, quotes_df):
    """根据筛选条件筛选股票"""
    print("正在筛选符合买入条件的股票...")
    
    filtered_stocks = []
    
    for _, row in quotes_df.iterrows():
        try:
            stock_code = str(row['代码'])
            stock_name = row['名称']
            
            if stock_code not in hs300_df['品种代码'].values:
                continue
            
            pe = row.get('市盈率-动态', None)
            pb = row.get('市净率', None)
            change_pct = row.get('涨跌幅', None)
            turnover = row.get('换手率', None)
            market_cap = row.get('流通市值', None)
            price = row.get('最新价', None)
            
            if pd.isna(change_pct) or pd.isna(price):
                continue
            
            conditions_met = []
            condition_details = []
            
            if pd.notna(pe) and pe < 30:
                conditions_met.append(True)
                condition_details.append(f"PE={pe:.2f}<30")
            else:
                conditions_met.append(False)
                
            if pd.notna(pb) and pb < 3:
                conditions_met.append(True)
                condition_details.append(f"PB={pb:.2f}<3")
            else:
                conditions_met.append(False)
                
            if change_pct > 0:
                conditions_met.append(True)
                condition_details.append(f"涨幅={change_pct:.2f}%>0")
            else:
                conditions_met.append(False)
                
            if pd.notna(turnover) and turnover > 1:
                conditions_met.append(True)
                condition_details.append(f"换手率={turnover:.2f}%>1%")
            else:
                conditions_met.append(False)
                
            if pd.notna(market_cap):
                market_cap_yi = market_cap / 1e8
                if 100 <= market_cap_yi <= 1000:
                    conditions_met.append(True)
                    condition_details.append(f"流通市值={market_cap_yi:.2f}亿(100-1000亿)")
                else:
                    conditions_met.append(False)
            else:
                conditions_met.append(False)
                
            if pd.notna(price) and price < 20:
                conditions_met.append(True)
                condition_details.append(f"股价={price:.2f}<20元")
            else:
                conditions_met.append(False)
            
            if sum(conditions_met) >= 3:
                filtered_stocks.append({
                    '代码': stock_code,
                    '名称': stock_name,
                    '最新价': price,
                    '涨跌幅': change_pct,
                    '市盈率': pe if pd.notna(pe) else None,
                    '市净率': pb if pd.notna(pb) else None,
                    '换手率': turnover if pd.notna(turnover) else None,
                    '流通市值(亿)': market_cap / 1e8 if pd.notna(market_cap) else None,
                    '满足条件数': sum(conditions_met),
                    '条件详情': '; '.join(condition_details)
                })
        except Exception as e:
            continue
    
    return pd.DataFrame(filtered_stocks)

def calculate_score(row):
    """计算综合评分"""
    score = 0
    
    if row['满足条件数'] > 0:
        score += row['满足条件数'] * 20
    
    if pd.notna(row['市盈率']) and row['市盈率'] > 0:
        score += max(0, (30 - row['市盈率']) / 3)
    
    if pd.notna(row['市净率']) and row['市净率'] > 0:
        score += max(0, (3 - row['市净率']) * 10)
    
    if pd.notna(row['涨跌幅']) and row['涨跌幅'] > 0:
        score += min(row['涨跌幅'], 10)
    
    if pd.notna(row['换手率']):
        score += min(row['换手率'], 10)
    
    return round(score, 2)

def generate_report(filtered_df, report_date):
    """生成推荐报告"""
    report_file = f"/workspace/a_stock_recommendation_{report_date}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("A股市场分析报告 - 沪深300成分股买入机会推荐\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("【报告说明】\n")
        f.write("本报告基于沪深300指数成分股，筛选符合以下至少3条条件的优质标的：\n")
        f.write("- 市盈率（PE）小于30\n")
        f.write("- 市净率（PB）小于3\n")
        f.write("- 今日涨幅大于0（即今日上涨）\n")
        f.write("- 换手率大于1%\n")
        f.write("- 流通市值在100亿-1000亿之间\n")
        f.write("- 股价低于20元\n\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"【筛选结果汇总】\n")
        f.write(f"符合买入条件的股票数量: {len(filtered_df)} 只\n\n")
        
        if len(filtered_df) > 0:
            filtered_df_sorted = filtered_df.sort_values('综合评分', ascending=False)
            
            f.write("【推荐股票列表（按综合评分排序）】\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'排名':<4} {'代码':<8} {'名称':<10} {'最新价':<8} {'涨跌幅':<8} {'PE':<8} {'PB':<8} {'换手率':<8} {'流通市值(亿)':<12} {'评分':<6}\n")
            f.write("-" * 80 + "\n")
            
            for idx, (_, row) in enumerate(filtered_df_sorted.iterrows(), 1):
                pe_str = f"{row['市盈率']:.2f}" if pd.notna(row['市盈率']) else "N/A"
                pb_str = f"{row['市净率']:.2f}" if pd.notna(row['市净率']) else "N/A"
                turnover_str = f"{row['换手率']:.2f}%" if pd.notna(row['换手率']) else "N/A"
                market_cap_str = f"{row['流通市值(亿)']:.2f}" if pd.notna(row['流通市值(亿)']) else "N/A"
                
                f.write(f"{idx:<4} {row['代码']:<8} {row['名称']:<10} {row['最新价']:<8.2f} {row['涨跌幅']:<8.2f}% {pe_str:<8} {pb_str:<8} {turnover_str:<8} {market_cap_str:<12} {row['综合评分']:<6.2f}\n")
            
            f.write("-" * 80 + "\n\n")
            
            f.write("【重点推荐股票分析】\n")
            f.write("=" * 80 + "\n\n")
            
            top_stocks = filtered_df_sorted.head(min(10, len(filtered_df_sorted)))
            for idx, (_, row) in enumerate(top_stocks.iterrows(), 1):
                f.write(f"{idx}. {row['名称']}（{row['代码']}）\n")
                f.write(f"   当前价格: {row['最新价']:.2f}元\n")
                f.write(f"   涨跌幅: {row['涨跌幅']:.2f}%\n")
                f.write(f"   市盈率(PE): {pe_str if (pe_str := f"{row['市盈率']:.2f}") else 'N/A'}\n")
                f.write(f"   市净率(PB): {pb_str if (pb_str := f"{row['市净率']:.2f}") else 'N/A'}\n")
                f.write(f"   换手率: {turnover_str if (turnover_str := f"{row['换手率']:.2f}%") else 'N/A'}\n")
                f.write(f"   流通市值: {market_cap_str if (market_cap_str := f"{row['流通市值(亿)']:.2f}亿") else 'N/A'}\n")
                f.write(f"   满足条件: {row['条件详情']}\n")
                f.write(f"   综合评分: {row['综合评分']:.2f}\n")
                
                analysis = []
                if pd.notna(row['市盈率']) and row['市盈率'] < 15:
                    analysis.append("估值偏低，具有投资价值")
                elif pd.notna(row['市盈率']) and row['市盈率'] < 30:
                    analysis.append("估值合理")
                
                if pd.notna(row['市净率']) and row['市净率'] < 2:
                    analysis.append("资产价值被低估")
                
                if row['涨跌幅'] > 2:
                    analysis.append("今日走势强劲")
                elif row['涨跌幅'] > 0:
                    analysis.append("今日温和上涨")
                
                if pd.notna(row['换手率']) and row['换手率'] > 3:
                    analysis.append("交易活跃度高")
                
                f.write(f"   分析: {'; '.join(analysis) if analysis else '综合表现良好'}\n")
                f.write("\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("【风险提示】\n")
        f.write("=" * 80 + "\n")
        f.write("1. 本报告仅供参考，不构成投资建议，投资者应根据自身风险承受能力做出投资决策。\n")
        f.write("2. 市场有风险，投资需谨慎。股票价格受多种因素影响，存在波动风险。\n")
        f.write("3. 市盈率和市净率仅为参考指标，不能完全反映公司的真实价值和风险水平。\n")
        f.write("4. 过去的表现不代表未来的收益，投资者应进行充分的尽职调查。\n")
        f.write("5. 建议投资者关注公司的基本面、行业前景、宏观经济环境等因素。\n")
        f.write("6. 本报告数据来源于公开市场信息，数据的准确性和完整性不能完全保证。\n")
        f.write("7. 投资者应分散投资，降低单一股票带来的集中风险。\n")
        f.write("8. 对于高估值股票，应谨慎对待，避免追高买入。\n")
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
    
    return report_file

def main():
    """主函数"""
    report_date = datetime.now().strftime('%Y%m%d')
    
    print("开始A股市场分析...")
    print("=" * 60)
    
    hs300_df = get_hs300_stocks()
    if hs300_df is None:
        print("获取沪深300成分股失败，程序退出")
        return
    
    print(f"成功获取 {len(hs300_df)} 只沪深300成分股")
    
    quotes_df = get_realtime_quotes(hs300_df)
    if quotes_df is None:
        print("获取实时行情数据失败，程序退出")
        return
    
    print(f"成功获取 {len(quotes_df)} 只股票实时行情")
    
    filtered_df = filter_stocks(hs300_df, quotes_df)
    print(f"符合买入条件的股票数量: {len(filtered_df)} 只")
    
    if len(filtered_df) > 0:
        filtered_df['综合评分'] = filtered_df.apply(calculate_score, axis=1)
        report_file = generate_report(filtered_df, report_date)
        print(f"\n推荐报告已生成: {report_file}")
        print(f"推荐股票总数: {len(filtered_df)} 只")
        print("\n推荐股票预览:")
        print(filtered_df[['名称', '最新价', '涨跌幅', '满足条件数', '综合评分']].head(10))
    else:
        report_file = f"/workspace/a_stock_recommendation_{report_date}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("A股市场分析报告 - 沪深300成分股买入机会推荐\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write("【筛选结果】\n")
            f.write("本次筛选未找到符合买入条件的股票。\n")
            f.write("可能原因：\n")
            f.write("1. 今日市场整体表现不佳\n")
            f.write("2. 筛选条件较为严格\n")
            f.write("3. 数据获取不完整\n\n")
            f.write("建议：\n")
            f.write("- 适当放宽筛选条件\n")
            f.write("- 关注不同市场周期的投资机会\n")
            f.write("- 分散投资，降低风险\n")
            f.write("\n【风险提示】\n")
            f.write("1. 本报告仅供参考，不构成投资建议\n")
            f.write("2. 市场有风险，投资需谨慎\n")
            f.write("=" * 80 + "\n")
        print(f"\n报告已生成: {report_file}")
    
    print("=" * 60)
    print("分析完成！")

if __name__ == "__main__":
    main()
