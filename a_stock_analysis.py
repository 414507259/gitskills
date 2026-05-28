#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股沪深300成分股买入机会分析脚本
使用多数据源获取数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time
import warnings
import requests
import re
warnings.filterwarnings('ignore')

def get_hs300_constituents():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    try:
        df = ak.index_stock_cons_weight_csindex(symbol="000300")
        print(f"获取到 {len(df)} 只成分股")
        return df
    except Exception as e:
        print(f"获取成分股列表出错: {e}")
        return pd.DataFrame()

def get_realtime_quotes_sina(stock_codes):
    """通过新浪接口获取实时行情"""
    print("尝试通过新浪接口获取实时行情...")
    all_data = []
    
    batch_size = 100
    for i in range(0, len(stock_codes), batch_size):
        batch = stock_codes[i:i+batch_size]
        codes_str = ','.join([f"sh{code}" if code.startswith('6') else f"sz{code}" for code in batch])
        
        try:
            url = f"http://hq.sinajs.cn/list={codes_str}"
            headers = {
                'Referer': 'http://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            lines = response.text.strip().split('\n')
            for line in lines:
                match = re.search(r'hq_str_(sh|sz)(\d+)="(.*)"', line)
                if match:
                    prefix = match.group(1)
                    code = match.group(2)
                    data = match.group(3)
                    
                    if data:
                        fields = data.split(',')
                        if len(fields) >= 32:
                            try:
                                stock_info = {
                                    'code': code,
                                    'name': fields[0],
                                    'open': float(fields[1]),
                                    'pre_close': float(fields[2]),
                                    'price': float(fields[3]),
                                    'high': float(fields[4]),
                                    'low': float(fields[5]),
                                    'volume': float(fields[8]),
                                    'amount': float(fields[9]),
                                    'change_pct': None,
                                    'turnover_rate': None,
                                    'pe': None,
                                    'pb': None,
                                    'circ_mv': None
                                }
                                
                                if stock_info['pre_close'] > 0:
                                    stock_info['change_pct'] = round((stock_info['price'] - stock_info['pre_close']) / stock_info['pre_close'] * 100, 2)
                                
                                all_data.append(stock_info)
                            except:
                                continue
            
            print(f"已获取 {len(all_data)} 只股票数据", end='\r')
            time.sleep(0.3)
        except Exception as e:
            print(f"批次 {i//batch_size + 1} 获取失败: {e}")
            continue
    
    print(f"\n新浪接口成功获取 {len(all_data)} 只股票数据")
    return pd.DataFrame(all_data)

def get_stock_valuation_tencent(stock_codes):
    """通过腾讯接口获取股票估值信息"""
    print("正在通过腾讯接口获取估值信息...")
    stock_info_dict = {}
    
    batch_size = 50
    for i in range(0, len(stock_codes), batch_size):
        batch = stock_codes[i:i+batch_size]
        codes_str = ','.join([f"sh{code}" if code.startswith('6') else f"sz{code}" for code in batch])
        
        try:
            url = f"http://qt.gtimg.cn/q={codes_str}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://gu.qq.com/'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            lines = response.text.strip().split('\n')
            for line in lines:
                match = re.search(r'v_(sh|sz)(\d+)="(.*)"', line)
                if match:
                    prefix = match.group(1)
                    code = match.group(2)
                    data = match.group(3)
                    
                    if data:
                        fields = data.split('~')
                        if len(fields) >= 45:
                            try:
                                pe = float(fields[39]) if fields[39] and fields[39] != '0' else None
                                pb = float(fields[46]) if len(fields) > 46 and fields[46] and fields[46] != '0' else None
                                total_mv = float(fields[45]) if len(fields) > 45 and fields[45] else None
                                
                                stock_info_dict[code] = {
                                    'pe': pe if pe and pe > 0 else None,
                                    'pb': pb if pb and pb > 0 else None,
                                    'circ_mv': total_mv * 100000000 if total_mv else None
                                }
                            except:
                                continue
            
            print(f"已获取 {len(stock_info_dict)} 只股票估值信息", end='\r')
            time.sleep(0.3)
        except Exception as e:
            continue
    
    print(f"\n腾讯接口成功获取 {len(stock_info_dict)} 只股票估值信息")
    return stock_info_dict

def get_stock_valuation_sina(stock_codes):
    """通过新浪财经获取股票估值信息"""
    print("正在通过新浪财经获取估值信息...")
    stock_info_dict = {}
    
    for i, code in enumerate(stock_codes):
        try:
            print(f"获取估值进度: {i+1}/{len(stock_codes)}", end='\r')
            
            market = 'sh' if code.startswith('6') else 'sz'
            url = f"http://finance.sina.com.cn/realstock/company/{market}{code}/js/v2/basic_info.js"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://finance.sina.com.cn/'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = 'utf-8'
            
            content = response.text
            
            pe_match = re.search(r'pe_fq:"([^"]*)"', content)
            pb_match = re.search(r'pb_fq:"([^"]*)"', content)
            mv_match = re.search(r'circ_mv:"([^"]*)"', content)
            
            pe = float(pe_match.group(1)) if pe_match and pe_match.group(1) else None
            pb = float(pb_match.group(1)) if pb_match and pb_match.group(1) else None
            circ_mv = float(mv_match.group(1)) * 100000000 if mv_match and mv_match.group(1) else None
            
            stock_info_dict[code] = {
                'pe': pe if pe and pe > 0 else None,
                'pb': pb if pb and pb > 0 else None,
                'circ_mv': circ_mv
            }
            
            time.sleep(0.1)
        except:
            continue
    
    print(f"\n新浪财经成功获取 {len(stock_info_dict)} 只股票估值信息")
    return stock_info_dict

def filter_stocks(df):
    """筛选符合条件的股票"""
    print("\n开始筛选符合条件的股票...")
    
    filtered_stocks = []
    
    for idx, row in df.iterrows():
        conditions_met = 0
        condition_details = []
        
        try:
            pe = float(row['pe']) if pd.notna(row.get('pe')) and row.get('pe') not in ['-', '', None] and row.get('pe') != 0 else None
            pb = float(row['pb']) if pd.notna(row.get('pb')) and row.get('pb') not in ['-', '', None] and row.get('pb') != 0 else None
            change_pct = float(row['change_pct']) if pd.notna(row.get('change_pct')) and row.get('change_pct') not in ['-', '', None] else None
            turnover_rate = float(row['turnover_rate']) if pd.notna(row.get('turnover_rate')) and row.get('turnover_rate') not in ['-', '', None] else None
            circ_mv = float(row['circ_mv']) if pd.notna(row.get('circ_mv')) and row.get('circ_mv') not in ['-', '', None] else None
            price = float(row['price']) if pd.notna(row.get('price')) and row.get('price') not in ['-', '', None] else None
        except (ValueError, TypeError):
            continue
        
        if pe is not None and pe > 0 and pe < 30:
            conditions_met += 1
            condition_details.append(f"PE={pe:.2f}<30")
        
        if pb is not None and pb > 0 and pb < 3:
            conditions_met += 1
            condition_details.append(f"PB={pb:.2f}<3")
        
        if change_pct is not None and change_pct > 0:
            conditions_met += 1
            condition_details.append(f"涨幅={change_pct:.2f}%>0")
        
        if turnover_rate is not None and turnover_rate > 1:
            conditions_met += 1
            condition_details.append(f"换手率={turnover_rate:.2f}%>1%")
        
        if circ_mv is not None:
            circ_mv_yi = circ_mv / 100000000
            if 100 <= circ_mv_yi <= 1000:
                conditions_met += 1
                condition_details.append(f"流通市值={circ_mv_yi:.2f}亿")
        
        if price is not None and price > 0 and price < 20:
            conditions_met += 1
            condition_details.append(f"股价={price:.2f}元<20元")
        
        if conditions_met >= 3:
            stock_info = {
                'code': row['code'],
                'name': row.get('name', ''),
                'price': price,
                'change_pct': change_pct,
                'turnover_rate': turnover_rate,
                'pe': pe,
                'pb': pb,
                'circ_mv': circ_mv / 100000000 if circ_mv else None,
                'conditions_met': conditions_met,
                'condition_details': ', '.join(condition_details)
            }
            filtered_stocks.append(stock_info)
    
    result_df = pd.DataFrame(filtered_stocks)
    
    if not result_df.empty:
        result_df['score'] = result_df['conditions_met'] * 10.0
        if 'pe' in result_df.columns:
            mask = result_df['pe'].notna() & (result_df['pe'] > 0)
            result_df.loc[mask, 'score'] = result_df.loc[mask, 'score'] + (30 - result_df.loc[mask, 'pe']) * 0.5
        if 'change_pct' in result_df.columns:
            mask = result_df['change_pct'].notna() & (result_df['change_pct'] > 0)
            result_df.loc[mask, 'score'] = result_df.loc[mask, 'score'] + result_df.loc[mask, 'change_pct'] * 2
        result_df = result_df.sort_values('score', ascending=False)
    
    print(f"筛选出 {len(result_df)} 只符合条件的股票")
    return result_df

def generate_report(filtered_df, output_file, total_analyzed):
    """生成推荐报告"""
    print(f"\n正在生成报告: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("              A股沪深300成分股买入机会分析报告\n")
        f.write("=" * 80 + "\n")
        f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"分析指数: 沪深300 (000300)\n")
        f.write(f"分析股票数: {total_analyzed}\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("【筛选条件】(至少满足以下3条)\n")
        f.write("-" * 80 + "\n")
        f.write("  1. 市盈率(PE) < 30\n")
        f.write("  2. 市净率(PB) < 3\n")
        f.write("  3. 今日涨幅 > 0\n")
        f.write("  4. 换手率 > 1%\n")
        f.write("  5. 流通市值在100亿-1000亿之间\n")
        f.write("  6. 股价 < 20元\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("【推荐股票列表】(按综合评分排序)\n")
        f.write("-" * 80 + "\n")
        
        if filtered_df.empty:
            f.write("暂无符合条件的股票\n")
        else:
            f.write(f"共筛选出 {len(filtered_df)} 只符合条件的股票\n\n")
            
            for idx, row in filtered_df.iterrows():
                f.write(f"\n{'='*60}\n")
                f.write(f"【{row['name']}】({row['code']})\n")
                f.write(f"{'='*60}\n")
                f.write(f"  综合评分: {row['score']:.2f} 分\n")
                f.write(f"  满足条件数: {row['conditions_met']}/6\n")
                f.write(f"\n  【关键指标】\n")
                price_str = f"{row['price']:.2f}" if row['price'] is not None else "N/A"
                change_str = f"{row['change_pct']:.2f}" if row['change_pct'] is not None else "N/A"
                turnover_str = f"{row['turnover_rate']:.2f}" if row['turnover_rate'] is not None else "N/A"
                pe_str = f"{row['pe']:.2f}" if row['pe'] is not None else "N/A"
                pb_str = f"{row['pb']:.2f}" if row['pb'] is not None else "N/A"
                mv_str = f"{row['circ_mv']:.2f}" if row['circ_mv'] is not None else "N/A"
                
                f.write(f"    当前股价: {price_str} 元\n")
                f.write(f"    今日涨跌幅: {change_str}%\n")
                f.write(f"    换手率: {turnover_str}%\n")
                f.write(f"    市盈率(PE): {pe_str}\n")
                f.write(f"    市净率(PB): {pb_str}\n")
                f.write(f"    流通市值: {mv_str} 亿\n")
                f.write(f"\n  【满足的条件】\n")
                f.write(f"    {row['condition_details']}\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("【风险提示】\n")
        f.write("=" * 80 + "\n")
        f.write("  1. 本报告仅供参考，不构成投资建议。\n")
        f.write("  2. 股市有风险，投资需谨慎。\n")
        f.write("  3. 历史表现不代表未来收益，请结合自身风险承受能力做出决策。\n")
        f.write("  4. 建议结合公司基本面、行业趋势、宏观经济等多方面因素综合分析。\n")
        f.write("  5. 数据来源于公开渠道，可能存在延迟或误差。\n")
        f.write("=" * 80 + "\n")
    
    print(f"报告已生成: {output_file}")

def main():
    print("=" * 60)
    print("A股沪深300成分股买入机会分析")
    print("=" * 60)
    
    hs300_df = get_hs300_constituents()
    
    if hs300_df.empty:
        print("获取沪深300成分股失败")
        return
    
    stock_codes = hs300_df['成分券代码'].tolist()
    stock_names = dict(zip(hs300_df['成分券代码'], hs300_df['成分券名称']))
    
    print("\n尝试获取实时行情数据...")
    realtime_df = pd.DataFrame()
    
    realtime_df = get_realtime_quotes_sina(stock_codes)
    
    if not realtime_df.empty:
        for idx, row in realtime_df.iterrows():
            code = row['code']
            if code in stock_names:
                realtime_df.at[idx, 'name'] = stock_names[code]
        
        stock_info_dict = get_stock_valuation_tencent(stock_codes)
        
        if len(stock_info_dict) < len(stock_codes) * 0.5:
            print("腾讯接口数据不完整，尝试新浪财经接口...")
            sina_info = get_stock_valuation_sina(stock_codes)
            stock_info_dict.update(sina_info)
        
        for idx, row in realtime_df.iterrows():
            code = row['code']
            if code in stock_info_dict:
                info = stock_info_dict[code]
                if info.get('pe'):
                    realtime_df.at[idx, 'pe'] = info['pe']
                if info.get('pb'):
                    realtime_df.at[idx, 'pb'] = info['pb']
                if info.get('circ_mv'):
                    realtime_df.at[idx, 'circ_mv'] = info['circ_mv']
    
    if realtime_df.empty:
        print("获取行情数据失败，无法继续分析")
        today = datetime.now().strftime('%Y%m%d')
        output_file = f"a_stock_recommendation_{today}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("              A股沪深300成分股买入机会分析报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            f.write("【错误信息】\n")
            f.write("无法获取实时行情数据，可能是网络连接问题或数据源暂时不可用。\n")
            f.write("请稍后重试或检查网络连接。\n")
        return
    
    filtered_df = filter_stocks(realtime_df)
    
    today = datetime.now().strftime('%Y%m%d')
    output_file = f"a_stock_recommendation_{today}.txt"
    
    generate_report(filtered_df, output_file, len(realtime_df))
    
    print("\n分析完成！")

if __name__ == "__main__":
    main()
