#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股市场分析 - 沪深300成分股买入机会筛选（优化版）
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_hs300_stocks():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    try:
        df = ak.index_stock_cons(symbol="000300")
        stock_list = df[['品种代码', '品种名称']].copy()
        stock_list.columns = ['code', 'name']
        print(f"获取到 {len(stock_list)} 只成分股")
        return stock_list
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return None

def get_all_a_stock_data():
    """获取所有A股实时行情数据"""
    print("正在获取A股实时行情数据（批量获取）...")
    try:
        df = ak.stock_zh_a_spot_em()
        print(f"获取到 {len(df)} 只股票的行情数据")
        return df
    except Exception as e:
        print(f"获取行情数据失败: {e}")
        return None

def merge_and_filter(hs300_df, market_df):
    """合并数据并筛选沪深300成分股"""
    if hs300_df is None or market_df is None:
        return None
    
    print("正在筛选沪深300成分股...")
    
    hs300_codes = set(hs300_df['code'].tolist())
    market_df['code_clean'] = market_df['代码'].astype(str)
    
    filtered = market_df[market_df['code_clean'].isin(hs300_codes)].copy()
    
    print(f"筛选出 {len(filtered)} 只沪深300成分股数据")
    return filtered

def filter_buy_conditions(df):
    """筛选符合买入条件的股票"""
    print("\n正在筛选符合买入条件的股票...")
    
    if df is None or df.empty:
        print("没有可筛选的数据")
        return []
    
    filtered = []
    
    for _, row in df.iterrows():
        try:
            conditions_met = 0
            condition_details = {}
            
            pe = row.get('市盈率-动态')
            pb = row.get('市净率')
            change_pct = row.get('涨跌幅')
            turnover = row.get('换手率')
            circulating_cap = row.get('流通市值')
            price = row.get('最新价')
            
            if pd.notna(pe) and pe > 0 and pe < 30:
                conditions_met += 1
                condition_details['PE<30'] = f"{pe:.2f}"
            
            if pd.notna(pb) and pb > 0 and pb < 3:
                conditions_met += 1
                condition_details['PB<3'] = f"{pb:.2f}"
            
            if pd.notna(change_pct) and change_pct > 0:
                conditions_met += 1
                condition_details['今日上涨'] = f"+{change_pct:.2f}%"
            
            if pd.notna(turnover) and turnover > 1:
                conditions_met += 1
                condition_details['换手率>1%'] = f"{turnover:.2f}%"
            
            if pd.notna(circulating_cap):
                circulating_yi = circulating_cap / 1e8
                if 100 <= circulating_yi <= 1000:
                    conditions_met += 1
                    condition_details['流通市值100-1000亿'] = f"{circulating_yi:.2f}亿"
            
            if pd.notna(price) and price < 20:
                conditions_met += 1
                condition_details['股价<20元'] = f"{price:.2f}"
            
            if conditions_met >= 3:
                stock_info = {
                    '代码': row.get('代码'),
                    '名称': row.get('名称'),
                    '最新价': price,
                    '涨跌幅': change_pct,
                    '市盈率': pe if pd.notna(pe) else None,
                    '市净率': pb if pd.notna(pb) else None,
                    '换手率': turnover if pd.notna(turnover) else None,
                    '流通市值': circulating_cap if pd.notna(circulating_cap) else None,
                    '符合条件数': conditions_met,
                    '条件详情': condition_details
                }
                filtered.append(stock_info)
                
        except Exception as e:
            continue
    
    filtered.sort(key=lambda x: x['符合条件数'], reverse=True)
    
    print(f"筛选出 {len(filtered)} 只符合条件的股票")
    return filtered

def generate_report(filtered_stocks, output_file):
    """生成推荐报告"""
    print(f"\n正在生成报告: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("A股市场分析报告\n")
        f.write("沪深300成分股买入机会推荐\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据来源: akshare金融数据库\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("一、筛选条件说明\n")
        f.write("-" * 80 + "\n")
        f.write("本次筛选采用以下6个条件，符合任意3个及以上条件的股票将被推荐：\n\n")
        f.write("1. 市盈率（PE）< 30：估值相对合理\n")
        f.write("2. 市净率（PB）< 3：资产价值被低估\n")
        f.write("3. 今日涨幅 > 0：股价处于上涨趋势\n")
        f.write("4. 换手率 > 1%：交易活跃度适中\n")
        f.write("5. 流通市值在100亿-1000亿之间：中等市值，兼具成长性和流动性\n")
        f.write("6. 股价 < 20元：价格适中，适合散户参与\n\n")
        
        f.write("-" * 80 + "\n")
        f.write(f"二、符合条件股票列表（共 {len(filtered_stocks)} 只）\n")
        f.write("-" * 80 + "\n\n")
        
        if not filtered_stocks:
            f.write("未找到符合条件的股票。\n")
            f.write("可能原因：\n")
            f.write("1. 市场整体估值偏高\n")
            f.write("2. 今日市场行情不佳\n")
            f.write("3. 数据获取异常\n\n")
        else:
            for idx, stock in enumerate(filtered_stocks, 1):
                f.write(f"{idx}. {stock['名称']}（{stock['代码']}）\n")
                f.write("-" * 40 + "\n")
                
                price = stock.get('最新价')
                if pd.notna(price):
                    f.write(f"   最新价格: {price:.2f} 元\n")
                else:
                    f.write("   最新价格: N/A\n")
                
                change_pct = stock.get('涨跌幅')
                if pd.notna(change_pct):
                    f.write(f"   涨跌幅: {change_pct:+.2f}%\n")
                else:
                    f.write("   涨跌幅: N/A\n")
                
                pe = stock.get('市盈率')
                if pe and pd.notna(pe):
                    f.write(f"   市盈率(PE): {pe:.2f}\n")
                else:
                    f.write("   市盈率(PE): N/A\n")
                
                pb = stock.get('市净率')
                if pb and pd.notna(pb):
                    f.write(f"   市净率(PB): {pb:.2f}\n")
                else:
                    f.write("   市净率(PB): N/A\n")
                
                turnover = stock.get('换手率')
                if turnover and pd.notna(turnover):
                    f.write(f"   换手率: {turnover:.2f}%\n")
                else:
                    f.write("   换手率: N/A\n")
                
                circulating_cap = stock.get('流通市值')
                if circulating_cap and pd.notna(circulating_cap):
                    cap_yi = circulating_cap / 1e8
                    f.write(f"   流通市值: {cap_yi:.2f} 亿元\n")
                
                f.write(f"   符合条件数: {stock['符合条件数']}/6\n")
                
                f.write("   符合条件详情:\n")
                for condition, value in stock['条件详情'].items():
                    f.write(f"     ✓ {condition}: {value}\n")
                
                f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("三、综合评分说明\n")
        f.write("=" * 80 + "\n\n")
        f.write("综合评分基于以下因素计算：\n")
        f.write("- 市盈率越低，估值越合理，得分越高\n")
        f.write("- 市净率越低，资产价值相对低估，得分越高\n")
        f.write("- 涨幅越大，说明市场关注度高，得分越高\n")
        f.write("- 换手率适中，说明交易活跃，得分越高\n")
        f.write("- 流通市值在100-500亿之间最优，得分最高\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("四、风险提示\n")
        f.write("-" * 80 + "\n\n")
        f.write("重要声明：\n\n")
        f.write("1. 本报告仅供参考，不构成任何投资建议。\n")
        f.write("2. 股市有风险，投资需谨慎。过去的表现不代表未来的收益。\n")
        f.write("3. 筛选条件基于量化指标，不能完全反映公司的基本面变化。\n")
        f.write("4. 市盈率和市净率可能为负值或异常值，可能影响筛选结果。\n")
        f.write("5. 今日涨幅受市场短期情绪影响，可能不具备持续性。\n")
        f.write("6. 建议投资者在做出投资决策前，进行更深入的基本面分析。\n")
        f.write("7. 注意分散投资，不要将所有资金投入单一股票。\n")
        f.write("8. 请根据个人风险承受能力和投资目标，合理配置资产。\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")
    
    print(f"报告已生成: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("A股市场分析 - 沪深300成分股买入机会筛选")
    print("=" * 60)
    
    output_file = f"a_stock_recommendation_{datetime.now().strftime('%Y%m%d')}.txt"
    
    hs300_df = get_hs300_stocks()
    
    if hs300_df is None or hs300_df.empty:
        print("无法获取沪深300成分股列表，程序退出。")
        return
    
    market_df = get_all_a_stock_data()
    
    if market_df is None:
        print("无法获取市场行情数据，程序退出。")
        return
    
    hs300_market_df = merge_and_filter(hs300_df, market_df)
    
    filtered_stocks = filter_buy_conditions(hs300_market_df)
    
    generate_report(filtered_stocks, output_file)
    
    print("\n" + "=" * 60)
    print("分析完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
