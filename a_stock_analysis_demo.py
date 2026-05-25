#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股沪深300成分股买入机会分析 - 演示版本
使用模拟数据展示脚本功能
在实际环境中可自动获取真实数据
"""

import pandas as pd
import numpy as np
from datetime import datetime
import random

def generate_sample_data():
    """生成模拟数据用于演示"""
    np.random.seed(42)
    random.seed(42)
    
    hs300_stocks = [
        {'代码': '600519', '名称': '贵州茅台', '最新价': 1680.00, '涨跌幅': 1.25, 
         '市盈率-动态': 35.2, '市净率': 11.5, '换手率': 0.85, '流通市值亿': 2100},
        {'代码': '600036', '名称': '招商银行', '最新价': 35.60, '涨跌幅': 0.85, 
         '市盈率-动态': 7.8, '市净率': 1.2, '换手率': 1.25, '流通市值亿': 890},
        {'代码': '000858', '名称': '五粮液', '最新价': 145.30, '涨跌幅': 1.56, 
         '市盈率-动态': 22.5, '市净率': 5.8, '换手率': 1.85, '流通市值亿': 560},
        {'代码': '601318', '名称': '中国平安', '最新价': 48.90, '涨跌幅': 0.65, 
         '市盈率-动态': 12.3, '市净率': 1.8, '换手率': 1.15, '流通市值亿': 890},
        {'代码': '600887', '名称': '伊利股份', '最新价': 27.80, '涨跌幅': 2.15, 
         '市盈率-动态': 18.5, '市净率': 4.2, '换手率': 2.35, '流通市值亿': 450},
        {'代码': '000333', '名称': '美的集团', '最新价': 62.50, '涨跌幅': 1.12, 
         '市盈率-动态': 15.8, '市净率': 3.5, '换手率': 1.45, '流通市值亿': 780},
        {'代码': '002415', '名称': '海康威视', '最新价': 32.40, '涨跌幅': 0.95, 
         '市盈率-动态': 28.5, '市净率': 5.2, '换手率': 1.65, '流通市值亿': 520},
        {'代码': '600900', '名称': '长江电力', '最新价': 18.90, '涨跌幅': 0.45, 
         '市盈率-动态': 22.0, '市净率': 2.8, '换手率': 0.85, '流通市值亿': 820},
        {'代码': '601888', '名称': '中国中免', '最新价': 72.60, '涨跌幅': 1.85, 
         '市盈率-动态': 32.5, '市净率': 8.5, '换手率': 2.25, '流通市值亿': 680},
        {'代码': '002714', '名称': '牧原股份', '最新价': 48.20, '涨跌幅': -0.75, 
         '市盈率-动态': 45.2, '市净率': 4.8, '换手率': 1.95, '流通市值亿': 620},
        {'代码': '600276', '名称': '恒瑞医药', '最新价': 52.30, '涨跌幅': 1.45, 
         '市盈率-动态': 65.5, '市净率': 8.2, '换手率': 1.35, '流通市值亿': 890},
        {'代码': '000651', '名称': '格力电器', '最新价': 38.50, '涨跌幅': 1.68, 
         '市盈率-动态': 12.5, '市净率': 2.5, '换手率': 2.15, '流通市值亿': 580},
        {'代码': '601166', '名称': '兴业银行', '最新价': 17.80, '涨跌幅': 0.92, 
         '市盈率-动态': 5.8, '市净率': 0.85, '换手率': 1.05, '流通市值亿': 720},
        {'代码': '600030', '名称': '中信证券', '最新价': 22.50, '涨跌幅': 1.35, 
         '市盈率-动态': 18.2, '市净率': 1.65, '换手率': 2.45, '流通市值亿': 650},
        {'代码': '600585', '名称': '海螺水泥', '最新价': 28.90, '涨跌幅': 1.78, 
         '市盈率-动态': 8.5, '市净率': 1.35, '换手率': 1.85, '流通市值亿': 420},
        {'代码': '000002', '名称': '万科A', '最新价': 12.30, '涨跌幅': -1.25, 
         '市盈率-动态': 8.2, '市净率': 0.75, '换手率': 2.25, '流通市值亿': 380},
        {'代码': '600690', '名称': '海尔智家', '最新价': 25.60, '涨跌幅': 1.92, 
         '市盈率-动态': 14.5, '市净率': 2.85, '换手率': 1.55, '流通市值亿': 510},
        {'代码': '601398', '名称': '工商银行', '最新价': 5.80, '涨跌幅': 0.35, 
         '市盈率-动态': 5.2, '市净率': 0.68, '换手率': 0.45, '流通市值亿': 1850},
        {'代码': '600048', '名称': '保利发展', '最新价': 14.50, '涨跌幅': 2.15, 
         '市盈率-动态': 9.8, '市净率': 1.05, '换手率': 2.65, '流通市值亿': 480},
        {'代码': '002594', '名称': '比亚迪', '最新价': 268.50, '涨跌幅': 1.25, 
         '市盈率-动态': 42.5, '市净率': 6.8, '换手率': 1.85, '流通市值亿': 1580},
        {'代码': '601628', '名称': '中国人寿', '最新价': 32.80, '涨跌幅': 0.78, 
         '市盈率-动态': 18.5, '市净率': 2.15, '换手率': 0.95, '流通市值亿': 950},
        {'代码': '600150', '名称': '中国船舶', '最新价': 38.90, '涨跌幅': 2.85, 
         '市盈率-动态': 25.5, '市净率': 2.45, '换手率': 3.25, '流通市值亿': 620},
        {'代码': '600570', '名称': '恒生电子', '最新价': 58.20, '涨跌幅': 1.68, 
         '市盈率-动态': 85.5, '市净率': 12.5, '换手率': 2.15, '流通市值亿': 320},
        {'代码': '601601', '名称': '中国太保', '最新价': 28.50, '涨跌幅': 0.92, 
         '市盈率-动态': 14.2, '市净率': 1.85, '换手率': 1.05, '流通市值亿': 720},
        {'代码': '000001', '名称': '平安银行', '最新价': 12.40, '涨跌幅': 1.05, 
         '市盈率-动态': 6.5, '市净率': 0.72, '换手率': 1.35, '流通市值亿': 580},
        {'代码': '601668', '名称': '中国建筑', '最新价': 6.20, '涨跌幅': 0.45, 
         '市盈率-动态': 5.8, '市净率': 0.92, '换手率': 0.85, '流通市值亿': 1200},
        {'代码': '600585', '名称': '华鲁恒升', '最新价': 28.60, '涨跌幅': 1.85, 
         '市盈率-动态': 12.5, '市净率': 2.65, '换手率': 2.15, '流通市值亿': 280},
        {'代码': '600019', '名称': '宝钢股份', '最新价': 7.80, '涨跌幅': 0.95, 
         '市盈率-动态': 9.2, '市净率': 0.85, '换手率': 1.25, '流通市值亿': 650},
        {'代码': '601857', '名称': '中国石油', '最新价': 8.50, '涨跌幅': 0.65, 
         '市盈率-动态': 8.5, '市净率': 0.95, '换手率': 0.55, '流通市值亿': 1580},
        {'代码': '601088', '名称': '中国神华', '最新价': 32.80, '涨跌幅': 1.15, 
         '市盈率-动态': 10.5, '市净率': 1.45, '换手率': 1.15, '流通市值亿': 820},
    ]
    
    return pd.DataFrame(hs300_stocks)

def calculate_comprehensive_score(row):
    """计算综合评分"""
    score = 0
    
    # PE评分
    pe = row.get('市盈率-动态')
    if pd.notna(pe) and pe > 0 and pe < 30:
        score += (30 - pe) / 30 * 25
    
    # PB评分
    pb = row.get('市净率')
    if pd.notna(pb) and pb < 3:
        score += (3 - pb) / 3 * 25
    
    # 涨幅评分
    change = row.get('涨跌幅')
    if pd.notna(change):
        if change > 0:
            score += 20
        else:
            score += max(0, change + 10)
    
    # 换手率评分
    turnover = row.get('换手率')
    if pd.notna(turnover) and turnover > 1:
        score += min(turnover * 5, 15)
    
    # 股价评分
    price = row.get('最新价')
    if pd.notna(price) and price < 20:
        score += 15
    
    return score

def analyze_and_filter_stocks():
    """分析并筛选股票"""
    print("=" * 80)
    print("说明：由于当前环境网络限制，使用模拟数据进行演示")
    print("在实际环境中，脚本会自动从akshare获取真实的沪深300数据")
    print("=" * 80)
    
    print("\n正在生成沪深300成分股模拟数据...")
    filtered_df = generate_sample_data()
    print(f"成功生成 {len(filtered_df)} 只股票的模拟数据")
    
    print("\n正在筛选符合买入条件的股票...")
    print("筛选条件:")
    print("1. 市盈率(PE) < 30")
    print("2. 市净率(PB) < 3")
    print("3. 今日涨幅 > 0")
    print("4. 换手率 > 1%")
    print("5. 流通市值: 100亿-1000亿")
    print("6. 股价 < 20元")
    
    # 应用筛选条件
    filtered_df = filtered_df[
        (filtered_df['市盈率-动态'] > 0) & 
        (filtered_df['市盈率-动态'] < 30)
    ]
    filtered_df = filtered_df[filtered_df['市净率'] < 3]
    filtered_df = filtered_df[filtered_df['涨跌幅'] > 0]
    filtered_df = filtered_df[filtered_df['换手率'] > 1]
    filtered_df = filtered_df[
        (filtered_df['流通市值亿'] >= 100) & 
        (filtered_df['流通市值亿'] <= 1000)
    ]
    filtered_df = filtered_df[filtered_df['最新价'] < 20]
    
    print(f"\n初步筛选后剩余 {len(filtered_df)} 只股票")
    
    if len(filtered_df) > 0:
        filtered_df['综合评分'] = filtered_df.apply(calculate_comprehensive_score, axis=1)
        filtered_df = filtered_df.sort_values('综合评分', ascending=False)
    
    return filtered_df

def generate_report(filtered_df, filename):
    """生成推荐报告"""
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("A股沪深300成分股买入机会分析报告\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {report_date}\n")
        f.write(f"数据来源: akshare实时行情（演示版本使用模拟数据）\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("一、筛选条件说明\n")
        f.write("=" * 80 + "\n")
        f.write("本报告从沪深300成分股中筛选符合以下条件的股票:\n\n")
        f.write("1. 市盈率(PE) < 30 - 估值合理\n")
        f.write("2. 市净率(PB) < 3 - 估值较低\n")
        f.write("3. 今日涨幅 > 0 - 今日股价上涨\n")
        f.write("4. 换手率 > 1% - 交易活跃度适中\n")
        f.write("5. 流通市值: 100亿-1000亿 - 中大盘股，流动性好\n")
        f.write("6. 股价 < 20元 - 价格适中，适合布局\n\n")
        f.write("注: 同时满足以上6条条件的股票，按综合评分从高到低排序\n\n")
        
        if filtered_df is None or len(filtered_df) == 0:
            f.write("=" * 80 + "\n")
            f.write("二、符合条件股票列表\n")
            f.write("=" * 80 + "\n\n")
            f.write("本次筛选未找到完全符合买入条件的股票。\n")
            f.write("可能原因:\n")
            f.write("1. 今日市场整体表现较弱\n")
            f.write("2. 沪深300成分股中同时满足多个条件的股票较少\n")
            f.write("3. 实时数据获取不完整\n\n")
        else:
            f.write("=" * 80 + "\n")
            f.write(f"二、符合条件股票列表（共 {len(filtered_df)} 只，按综合评分排序）\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"{'排名':<4} {'代码':<8} {'名称':<10} {'最新价':<8} {'涨跌幅':<8} "
                   f"{'PE':<8} {'PB':<6} {'换手率':<8} {'流通市值(亿)':<12} {'评分':<6}\n")
            f.write("-" * 100 + "\n")
            
            for idx, (_, row) in enumerate(filtered_df.iterrows(), 1):
                code = row.get('代码', 'N/A')
                name = row.get('名称', 'N/A')
                price = row.get('最新价', 0)
                change = row.get('涨跌幅', 0)
                pe = row.get('市盈率-动态', 0)
                pb = row.get('市净率', 0)
                turnover = row.get('换手率', 0)
                mktcap = row.get('流通市值亿', 0)
                score = row.get('综合评分', 0)
                
                f.write(f"{idx:<4} {code:<8} {name:<10} {price:<8.2f} {change:<7.2f}% "
                       f"{pe:<8.2f} {pb:<6.2f} {turnover:<7.2f}% {mktcap:<12.2f} {score:<6.2f}\n")
            
            f.write("\n")
            
            f.write("=" * 80 + "\n")
            f.write("三、每只股票关键指标分析\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, (_, row) in enumerate(filtered_df.iterrows(), 1):
                f.write(f"{idx}. {row.get('名称', 'N/A')} ({row.get('代码', 'N/A')})\n")
                f.write("-" * 60 + "\n")
                
                price = row.get('最新价', 0)
                change = row.get('涨跌幅', 0)
                pe = row.get('市盈率-动态', 0)
                pb = row.get('市净率', 0)
                turnover = row.get('换手率', 0)
                mktcap = row.get('流通市值亿', 0)
                score = row.get('综合评分', 0)
                
                f.write(f"   最新价: {price:.2f}元\n")
                f.write(f"   涨跌幅: {change:+.2f}%\n")
                f.write(f"   市盈率(PE): {pe:.2f}\n")
                f.write(f"   市净率(PB): {pb:.2f}\n")
                f.write(f"   换手率: {turnover:.2f}%\n")
                f.write(f"   流通市值: {mktcap:.2f}亿元\n")
                f.write(f"   综合评分: {score:.2f}/100\n")
                
                satisfied_conditions = []
                if pd.notna(pe) and 0 < pe < 30:
                    satisfied_conditions.append("✓ PE < 30")
                if pd.notna(pb) and pb < 3:
                    satisfied_conditions.append("✓ PB < 3")
                if pd.notna(change) and change > 0:
                    satisfied_conditions.append("✓ 今日上涨")
                if pd.notna(turnover) and turnover > 1:
                    satisfied_conditions.append("✓ 换手率 > 1%")
                if pd.notna(mktcap) and 100 <= mktcap <= 1000:
                    satisfied_conditions.append("✓ 流通市值适中")
                if pd.notna(price) and price < 20:
                    satisfied_conditions.append("✓ 股价 < 20元")
                
                f.write(f"   满足条件: {', '.join(satisfied_conditions)}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("四、风险提示\n")
        f.write("=" * 80 + "\n\n")
        f.write("重要声明:\n\n")
        f.write("1. 本报告仅供参考，不构成任何投资建议。\n")
        f.write("2. 股票投资有风险，入市需谨慎。\n")
        f.write("3. 过去的表现不代表未来的收益。\n")
        f.write("4. 单一指标选股存在局限性，建议结合基本面和技术面综合分析。\n")
        f.write("5. PE和PB为动态指标，可能存在滞后或不准确的情况。\n")
        f.write("6. 市场环境、行业周期、公司经营状况等因素都会影响股价表现。\n")
        f.write("7. 建议投资者根据自身风险承受能力合理配置资产。\n\n")
        f.write("免责声明:\n")
        f.write("本报告中的信息来源于公开数据，编制者不对信息的准确性和完整性做任何保证。\n")
        f.write("投资者根据本报告做出的任何投资决策，自行承担风险。\n\n")
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")
    
    print(f"\n报告已生成: {filename}")

def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("A股沪深300成分股买入机会分析系统")
    print("=" * 80 + "\n")
    
    filtered_df = analyze_and_filter_stocks()
    
    report_date = datetime.now().strftime("%Y%m%d")
    filename = f"a_stock_recommendation_{report_date}.txt"
    generate_report(filtered_df, filename)
    
    print("\n分析完成！")
    print(f"推荐报告已保存至: {filename}")
    print("\n提示：在有网络连接的环境中，可以运行 a_stock_analysis_v2.py 获取真实数据")

if __name__ == "__main__":
    main()
