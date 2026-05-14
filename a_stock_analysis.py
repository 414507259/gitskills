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
            high_price = row.get('最高价', None)
            low_price = row.get('最低价', None)
            volume = row.get('成交量', None)
            amount = row.get('成交额', None)
            
            if pd.isna(change_pct) or pd.isna(price):
                continue
            
            conditions_met = []
            condition_details = []
            
            if pd.notna(pe) and 0 < pe < 30:
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
                    condition_details.append(f"流通市值={market_cap_yi:.2f}亿")
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
                    '市盈率': pe if pd.notna(pe) and pe > 0 else None,
                    '市净率': pb if pd.notna(pb) and pb > 0 else None,
                    '换手率': turnover if pd.notna(turnover) else None,
                    '流通市值(亿)': market_cap / 1e8 if pd.notna(market_cap) else None,
                    '最高价': high_price,
                    '最低价': low_price,
                    '成交量': volume,
                    '成交额': amount,
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

def generate_buy_recommendation(row):
    """生成个股购买建议"""
    recommendations = []
    risk_level = "低"
    
    if pd.notna(row['市盈率']) and row['市盈率'] > 0:
        if row['市盈率'] < 15:
            recommendations.append("估值极低，投资价值显著")
            risk_level = "低"
        elif row['市盈率'] < 25:
            recommendations.append("估值合理，具有安全边际")
            risk_level = "中低"
        elif row['市盈率'] < 40:
            recommendations.append("估值偏高，建议谨慎")
            risk_level = "中"
    
    if pd.notna(row['市净率']) and row['市净率'] > 0:
        if row['市净率'] < 1.5:
            recommendations.append("资产被低估")
        elif row['市净率'] < 2.5:
            recommendations.append("资产价值合理")
    
    if pd.notna(row['涨跌幅']):
        if row['涨跌幅'] > 5:
            recommendations.append("今日涨幅过大，追高风险较高")
            risk_level = "高" if risk_level == "中" else "中"
        elif row['涨跌幅'] > 2:
            recommendations.append("今日走势强劲，可关注")
        elif row['涨跌幅'] > 0:
            recommendations.append("今日温和上涨，趋势向好")
    
    if pd.notna(row['换手率']):
        if row['换手率'] > 5:
            recommendations.append("交易非常活跃，波动可能较大")
        elif row['换手率'] > 2:
            recommendations.append("交易活跃度良好")
    
    if pd.notna(row['流通市值(亿)']):
        if 200 <= row['流通市值(亿)'] <= 500:
            recommendations.append("中等市值，兼具流动性与成长性")
        elif row['流通市值(亿)'] > 500:
            recommendations.append("大盘蓝筹，稳健之选")
    
    investment_rating = "A" if risk_level == "低" else "B" if risk_level == "中低" else "C" if risk_level == "中" else "D"
    
    return {
        '建议': '; '.join(recommendations) if recommendations else '综合表现良好',
        '风险等级': risk_level,
        '投资评级': investment_rating,
        '建议买入价': round(row['最新价'] * 0.98, 2),
        '建议止损价': round(row['最新价'] * 0.95, 2),
        '建议止盈价': round(row['最新价'] * 1.15, 2),
        '建议仓位': '5%-10%' if risk_level == "低" else '3%-5%' if risk_level == "中低" else '1%-3%'
    }

def analyze_portfolio(portfolio_file):
    """分析持仓股票"""
    try:
        portfolio = pd.read_csv(portfolio_file, encoding='utf-8')
        print(f"成功读取持仓文件: {portfolio_file}")
        return portfolio
    except FileNotFoundError:
        print(f"持仓文件不存在: {portfolio_file}，将创建示例持仓")
        return create_sample_portfolio()
    except Exception as e:
        print(f"读取持仓文件失败: {e}")
        return create_sample_portfolio()

def create_sample_portfolio():
    """创建示例持仓"""
    sample_stocks = [
        {'股票代码': '600519', '股票名称': '贵州茅台', '持仓数量': 100, '成本价': 1650.00},
        {'股票代码': '000858', '股票名称': '五粮液', '持仓数量': 500, '成本价': 145.00},
        {'股票代码': '601318', '股票名称': '中国平安', '持仓数量': 1000, '成本价': 48.00},
        {'股票代码': '600036', '股票名称': '招商银行', '持仓数量': 2000, '成本价': 32.00},
        {'股票代码': '000333', '股票名称': '美的集团', '持仓数量': 800, '成本价': 58.00},
    ]
    return pd.DataFrame(sample_stocks)

def analyze_holdings(holdings_df, quotes_df):
    """分析持仓股票的表现"""
    print("正在分析持仓股票...")
    
    analysis_results = []
    
    for _, holding in holdings_df.iterrows():
        stock_code = str(holding['股票代码']).zfill(6)
        stock_name = holding['股票名称']
        quantity = holding['持仓数量']
        cost_price = holding['成本价']
        
        quote = quotes_df[quotes_df['代码'] == stock_code]
        
        if len(quote) > 0:
            current_price = quote.iloc[0]['最新价']
            change_pct = quote.iloc[0]['涨跌幅']
            pe = quote.iloc[0]['市盈率']
            pb = quote.iloc[0]['市净率']
            
            profit_loss = (current_price - cost_price) * quantity
            profit_loss_pct = ((current_price - cost_price) / cost_price) * 100
            
            if profit_loss >= 0:
                status = "盈利"
                status_emoji = "📈"
            else:
                status = "亏损"
                status_emoji = "📉"
            
            recommendations = []
            if profit_loss_pct < -10:
                recommendations.append("建议加仓摊薄成本")
            elif profit_loss_pct < -5:
                recommendations.append("建议持有观察")
            elif profit_loss_pct > 15:
                recommendations.append("建议考虑止盈")
            elif profit_loss_pct > 10:
                recommendations.append("建议设置移动止损")
            else:
                recommendations.append("建议耐心持有")
            
            if pd.notna(pe) and pe > 50:
                recommendations.append("估值偏高，关注风险")
            elif pd.notna(pe) and pe < 20:
                recommendations.append("估值合理，可继续持有")
            
            analysis_results.append({
                '股票代码': stock_code,
                '股票名称': stock_name,
                '持仓数量': quantity,
                '成本价': cost_price,
                '当前价': current_price,
                '涨跌幅': change_pct,
                '盈亏金额': profit_loss,
                '盈亏比例': profit_loss_pct,
                '状态': f"{status_emoji} {status}",
                '市盈率': pe,
                '市净率': pb,
                '持仓建议': '; '.join(recommendations)
            })
        else:
            analysis_results.append({
                '股票代码': stock_code,
                '股票名称': stock_name,
                '持仓数量': quantity,
                '成本价': cost_price,
                '当前价': 'N/A',
                '涨跌幅': 'N/A',
                '盈亏金额': 'N/A',
                '盈亏比例': 'N/A',
                '状态': '⚠️ 数据获取失败',
                '市盈率': 'N/A',
                '市净率': 'N/A',
                '持仓建议': '请手动更新数据'
            })
    
    return pd.DataFrame(analysis_results)

def calculate_portfolio_summary(holdings_analysis):
    """计算持仓汇总"""
    valid_holdings = holdings_analysis[holdings_analysis['盈亏金额'] != 'N/A']
    
    if len(valid_holdings) == 0:
        return {
            '总持仓数': len(holdings_analysis),
            '盈利股票数': 0,
            '亏损股票数': 0,
            '总盈亏金额': 0,
            '总盈亏比例': 0,
            '持仓总市值': 0,
            '总成本': 0
        }
    
    total_cost = sum(valid_holdings['成本价'] * valid_holdings['持仓数量'])
    total_market_value = sum(valid_holdings['当前价'] * valid_holdings['持仓数量'])
    total_profit_loss = total_market_value - total_cost
    total_profit_loss_pct = (total_profit_loss / total_cost * 100) if total_cost > 0 else 0
    
    profit_count = len(valid_holdings[valid_holdings['盈亏金额'] > 0])
    loss_count = len(valid_holdings[valid_holdings['盈亏金额'] < 0])
    
    return {
        '总持仓数': len(valid_holdings),
        '盈利股票数': profit_count,
        '亏损股票数': loss_count,
        '总盈亏金额': total_profit_loss,
        '总盈亏比例': total_profit_loss_pct,
        '持仓总市值': total_market_value,
        '总成本': total_cost
    }

def generate_report(filtered_df, holdings_analysis, portfolio_summary, report_date):
    """生成推荐报告"""
    report_file = f"/workspace/a_stock_recommendation_{report_date}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("A股市场分析报告 - 沪深300成分股买入机会推荐\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("【报告说明】\n")
        f.write("本报告基于沪深300指数成分股，筛选符合以下条件的优质标的：\n")
        f.write("- 市盈率（PE）小于30且大于0\n")
        f.write("- 市净率（PB）小于3\n")
        f.write("- 今日涨幅大于0\n")
        f.write("- 换手率大于1%\n")
        f.write("- 流通市值在100亿-1000亿之间\n")
        f.write("- 股价低于20元\n")
        f.write("注：股票必须同时满足至少3项条件\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("【第一部分：持仓股票分析】\n")
        f.write("=" * 80 + "\n\n")
        
        if len(holdings_analysis) > 0:
            f.write(f"持仓股票总数: {len(holdings_analysis)} 只\n")
            f.write(f"盈利股票数: {portfolio_summary['盈利股票数']} 只\n")
            f.write(f"亏损股票数: {portfolio_summary['亏损股票数']} 只\n")
            f.write(f"总成本: {portfolio_summary['总成本']:,.2f} 元\n")
            f.write(f"持仓总市值: {portfolio_summary['持仓总市值']:,.2f} 元\n")
            f.write(f"总盈亏: {portfolio_summary['总盈亏金额']:+,.2f} 元 ({portfolio_summary['总盈亏比例']:+.2f}%)\n\n")
            
            f.write("【持仓明细】\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'代码':<8} {'名称':<10} {'持仓量':<8} {'成本价':<10} {'当前价':<10} {'涨跌幅':<8} {'盈亏金额':<12} {'盈亏比例':<10} {'状态':<12}\n")
            f.write("-" * 80 + "\n")
            
            for _, row in holdings_analysis.iterrows():
                if row['盈亏金额'] != 'N/A':
                    f.write(f"{row['股票代码']:<8} {row['股票名称']:<10} {row['持仓数量']:<8} "
                           f"{row['成本价']:<10.2f} {row['当前价']:<10.2f} {row['涨跌幅']:<8.2f}% "
                           f"{row['盈亏金额']:<+12.2f} {row['盈亏比例']:<+10.2f}% {row['状态']:<12}\n")
                else:
                    f.write(f"{row['股票代码']:<8} {row['股票名称']:<10} {row['持仓数量']:<8} "
                           f"{row['成本价']:<10.2f} {'N/A':<10} {'N/A':<8} "
                           f"{'N/A':<12} {'N/A':<10} {row['状态']:<12}\n")
            
            f.write("-" * 80 + "\n\n")
            
            f.write("【持仓优化建议】\n")
            for _, row in holdings_analysis.iterrows():
                if row['盈亏金额'] != 'N/A':
                    f.write(f"{row['股票名称']}（{row['股票代码']}）: {row['持仓建议']}\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"【第二部分：筛选结果汇总】\n")
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
            
            f.write("【第三部分：个股购买建议详请】\n")
            f.write("=" * 80 + "\n\n")
            
            top_stocks = filtered_df_sorted.head(min(15, len(filtered_df_sorted)))
            for idx, (_, row) in enumerate(top_stocks.iterrows(), 1):
                buy_rec = generate_buy_recommendation(row)
                
                pe_str = f"{row['市盈率']:.2f}" if pd.notna(row['市盈率']) else 'N/A'
                pb_str = f"{row['市净率']:.2f}" if pd.notna(row['市净率']) else 'N/A'
                turnover_str = f"{row['换手率']:.2f}%" if pd.notna(row['换手率']) else 'N/A'
                market_cap_str = f"{row['流通市值(亿)']:.2f} 亿" if pd.notna(row['流通市值(亿)']) else 'N/A'
                
                f.write(f"{'★' * 3} {idx}. {row['名称']}（{row['代码']}）{'★' * 3}\n")
                f.write(f"   {'─' * 40}\n")
                f.write(f"   📊 当前价格: {row['最新价']:.2f} 元\n")
                f.write(f"   📈 涨跌幅: {row['涨跌幅']:.2f}%\n")
                f.write(f"   💰 市盈率(PE): {pe_str}\n")
                f.write(f"   💵 市净率(PB): {pb_str}\n")
                f.write(f"   🔄 换手率: {turnover_str}\n")
                f.write(f"   🏢 流通市值: {market_cap_str}\n")
                f.write(f"   ✓ 满足条件: {row['条件详情']}\n")
                f.write(f"   {'─' * 40}\n")
                f.write(f"   【投资评级】: {buy_rec['投资评级']} 级\n")
                f.write(f"   【风险等级】: {buy_rec['风险等级']}\n")
                f.write(f"   【综合建议】: {buy_rec['建议']}\n")
                f.write(f"   {'─' * 40}\n")
                f.write(f"   💡 操作建议:\n")
                f.write(f"      - 建议买入价: {buy_rec['建议买入价']} 元\n")
                f.write(f"      - 建议止损价: {buy_rec['建议止损价']} 元（下跌5%时止损）\n")
                f.write(f"      - 建议止盈价: {buy_rec['建议止盈价']} 元（上涨15%时考虑止盈）\n")
                f.write(f"      - 建议仓位: 单只股票仓位不超过 {buy_rec['建议仓位']}\n")
                f.write(f"   🎯 综合评分: {row['综合评分']:.2f}\n")
                f.write("\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("【第四部分：风险提示】\n")
        f.write("=" * 80 + "\n")
        f.write("1. 本报告仅供参考，不构成投资建议，投资者应根据自身风险承受能力做出投资决策。\n")
        f.write("2. 市场有风险，投资需谨慎。股票价格受多种因素影响，存在波动风险。\n")
        f.write("3. 市盈率和市净率仅为参考指标，不能完全反映公司的真实价值和风险水平。\n")
        f.write("4. 过去的表现不代表未来的收益，投资者应进行充分的尽职调查。\n")
        f.write("5. 建议投资者关注公司的基本面、行业前景、宏观经济环境等因素。\n")
        f.write("6. 本报告数据来源于公开市场信息，数据的准确性和完整性不能完全保证。\n")
        f.write("7. 投资者应分散投资，降低单一股票带来的集中风险。\n")
        f.write("8. 对于高估值股票，应谨慎对待，避免追高买入。\n")
        f.write("9. 止损和止盈建议仅为参考，实际操作应根据市场情况灵活调整。\n")
        f.write("10. 投资有赚有赔，应保持理性，不要因为短期波动而做出冲动决策。\n")
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
        f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
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
    
    portfolio_file = "/workspace/my_portfolio.csv"
    holdings_df = analyze_portfolio(portfolio_file)
    
    if len(holdings_df) > 0:
        holdings_analysis = analyze_holdings(holdings_df, quotes_df)
        portfolio_summary = calculate_portfolio_summary(holdings_analysis)
    else:
        holdings_analysis = pd.DataFrame()
        portfolio_summary = {
            '总持仓数': 0, '盈利股票数': 0, '亏损股票数': 0,
            '总盈亏金额': 0, '总盈亏比例': 0, '持仓总市值': 0, '总成本': 0
        }
    
    if len(filtered_df) > 0:
        filtered_df['综合评分'] = filtered_df.apply(calculate_score, axis=1)
    
    report_file = generate_report(filtered_df, holdings_analysis, portfolio_summary, report_date)
    print(f"\n推荐报告已生成: {report_file}")
    
    if len(filtered_df) > 0:
        print(f"\n推荐股票总数: {len(filtered_df)} 只")
        print("\n推荐股票预览（前10只）:")
        preview = filtered_df.copy()
        preview['综合评分'] = preview.apply(calculate_score, axis=1)
        preview_sorted = preview.sort_values('综合评分', ascending=False)
        print(preview_sorted[['名称', '最新价', '涨跌幅', '满足条件数', '综合评分']].head(10))
    
    if len(holdings_analysis) > 0:
        print("\n持仓分析预览:")
        for _, row in holdings_analysis.iterrows():
            if row['盈亏金额'] != 'N/A':
                print(f"  {row['股票名称']}: {row['状态']} {row['盈亏金额']:+,.2f}元 ({row['盈亏比例']:+.2f}%)")
    
    print("=" * 60)
    print("分析完成！")

if __name__ == "__main__":
    main()
