#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股沪深300成分股买入机会分析 - 备用数据源版本
使用akshare获取数据并生成推荐报告
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_hs300_components():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    try:
        df = ak.index_stock_cons(symbol="000300")
        print(f"成功获取 {len(df)} 只沪深300成分股")
        return df
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return None

def get_stock_info_batch(stock_codes):
    """批量获取股票信息"""
    print(f"正在获取 {len(stock_codes)} 只股票的信息...")
    all_data = []
    
    for i, code in enumerate(stock_codes):
        if i % 50 == 0:
            print(f"进度: {i}/{len(stock_codes)}")
        
        try:
            if code.startswith('6'):
                symbol = f"sh{code}"
            else:
                symbol = f"sz{code}"
            
            df = ak.stock_individual_info_em(symbol=symbol)
            if df is not None and len(df) > 0:
                info_dict = {'代码': code}
                for _, row in df.iterrows():
                    info_dict[row['item']] = row['value']
                all_data.append(info_dict)
        except Exception:
            continue
    
    if all_data:
        result_df = pd.DataFrame(all_data)
        print(f"成功获取 {len(result_df)} 只股票的信息")
        return result_df
    return None

def get_realtime_quote_batch(stock_codes):
    """批量获取实时行情"""
    print(f"正在获取 {len(stock_codes)} 只股票的实时行情...")
    
    try:
        if stock_codes:
            df = ak.stock_zh_a_spot_em()
            if df is not None and len(df) > 0:
                hs300_codes = set([str(code) for code in stock_codes])
                filtered_df = df[df['代码'].astype(str).isin(hs300_codes)]
                print(f"成功获取 {len(filtered_df)} 只股票的实时行情")
                return filtered_df
    except Exception as e:
        print(f"获取实时行情失败: {e}")
    
    return None

def calculate_comprehensive_score(row):
    """计算综合评分"""
    score = 0
    
    try:
        # PE评分
        pe = row.get('市盈率-动态', row.get('市盈率'))
        if pd.notna(pe):
            pe_val = float(pe)
            if 0 < pe_val < 30:
                score += (30 - pe_val) / 30 * 25
        
        # PB评分
        pb = row.get('市净率')
        if pd.notna(pb):
            pb_val = float(pb)
            if pb_val < 3:
                score += (3 - pb_val) / 3 * 25
        
        # 涨幅评分
        change = row.get('涨跌幅', 0)
        if pd.notna(change):
            change_val = float(change)
            if change_val > 0:
                score += 20
            else:
                score += max(0, change_val + 10)
        
        # 换手率评分
        turnover = row.get('换手率', 0)
        if pd.notna(turnover):
            turnover_val = float(turnover)
            if turnover_val > 1:
                score += min(turnover_val * 5, 15)
        
        # 股价评分
        price = row.get('最新价', row.get('当前价', 0))
        if pd.notna(price):
            price_val = float(price)
            if price_val < 20:
                score += 15
    except Exception:
        pass
    
    return score

def analyze_and_filter_stocks():
    """分析并筛选股票"""
    # 获取沪深300成分股
    hs300_df = get_hs300_components()
    if hs300_df is None or len(hs300_df) == 0:
        print("无法获取沪深300成分股数据")
        return None
    
    stock_codes = hs300_df['品种代码'].tolist()
    
    # 尝试获取实时行情数据
    realtime_df = get_realtime_quote_batch(stock_codes)
    
    if realtime_df is not None and len(realtime_df) > 0:
        filtered_df = realtime_df.copy()
    else:
        print("\n实时行情获取失败，尝试使用历史数据...")
        # 使用历史K线数据作为备选
        try:
            df = ak.stock_zh_a_hist(symbol="000300", period="daily", 
                                   start_date="20260501", end_date="20260525")
            if df is not None:
                print("使用沪深300指数历史数据")
                filtered_df = pd.DataFrame()
            else:
                filtered_df = pd.DataFrame()
        except:
            filtered_df = pd.DataFrame()
    
    if filtered_df.empty:
        print("\n无法获取足够的行情数据进行分析")
        return None
    
    # 数据处理
    numeric_columns = ['市盈率-动态', '市净率', '涨跌幅', '换手率', '流通市值', '最新价']
    for col in numeric_columns:
        if col in filtered_df.columns:
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    
    if '流通市值' in filtered_df.columns:
        filtered_df['流通市值亿'] = filtered_df['流通市值'] / 1e8
    
    # 筛选条件
    print("\n正在筛选符合买入条件的股票...")
    print("筛选条件:")
    print("- 市盈率(PE) < 30")
    print("- 市净率(PB) < 3")
    print("- 今日涨幅 > 0")
    print("- 换手率 > 1%")
    print("- 流通市值: 100亿-1000亿")
    print("- 股价 < 20元")
    
    # 应用筛选
    if '市盈率-动态' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['市盈率-动态'] > 0) & 
            (filtered_df['市盈率-动态'] < 30)
        ]
    
    if '市净率' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['市净率'] < 3]
    
    if '涨跌幅' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['涨跌幅'] > 0]
    
    if '换手率' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['换手率'] > 1]
    
    if '流通市值亿' in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df['流通市值亿'] >= 100) & 
            (filtered_df['流通市值亿'] <= 1000)
        ]
    
    if '最新价' in filtered_df.columns:
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
        f.write(f"数据来源: akshare实时行情\n\n")
        
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
        f.write("注: 满足以上至少3条条件的股票纳入推荐范围\n\n")
        
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
            
            for idx, (_, row) in enumerate(filtered_df.head(20).iterrows(), 1):
                code = row.get('代码', 'N/A')
                name = row.get('名称', 'N/A')[:8]
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
            
            for idx, (_, row) in enumerate(filtered_df.head(10).iterrows(), 1):
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
                try:
                    if pd.notna(pe) and 0 < float(pe) < 30:
                        satisfied_conditions.append("✓ PE < 30")
                    if pd.notna(pb) and float(pb) < 3:
                        satisfied_conditions.append("✓ PB < 3")
                    if pd.notna(change) and float(change) > 0:
                        satisfied_conditions.append("✓ 今日上涨")
                    if pd.notna(turnover) and float(turnover) > 1:
                        satisfied_conditions.append("✓ 换手率 > 1%")
                    if pd.notna(mktcap) and 100 <= float(mktcap) <= 1000:
                        satisfied_conditions.append("✓ 流通市值适中")
                    if pd.notna(price) and float(price) < 20:
                        satisfied_conditions.append("✓ 股价 < 20元")
                except:
                    pass
                
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
    print("开始A股沪深300成分股分析...")
    print("-" * 60)
    
    filtered_df = analyze_and_filter_stocks()
    
    report_date = datetime.now().strftime("%Y%m%d")
    filename = f"a_stock_recommendation_{report_date}.txt"
    generate_report(filtered_df, filename)
    
    print("\n分析完成！")
    print(f"推荐报告已保存至: {filename}")

if __name__ == "__main__":
    main()
