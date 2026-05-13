import akshare as ak
import pandas as pd
from datetime import datetime
import time


def get_hs300_constituents():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    hs300_df = ak.index_stock_cons(symbol="000300")
    print(f"成功获取 {len(hs300_df)} 只沪深300成分股")
    return hs300_df


def get_stock_realtime_data(symbol):
    """获取个股实时行情数据"""
    try:
        df = ak.stock_individual_info_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取 {symbol} 数据失败: {e}")
        return None


def get_batch_stock_data(stock_codes):
    """批量获取股票数据"""
    print("正在获取个股实时行情数据...")
    
    # 只调用一次获取全部A股行情
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    
    # 筛选出沪深300成分股
    stock_list = []
    for code in stock_codes:
        try:
            stock_data = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == code]
            
            if not stock_data.empty:
                stock_info = {
                    '代码': stock_data['代码'].values[0],
                    '名称': stock_data['名称'].values[0],
                    '最新价': stock_data['最新价'].values[0],
                    '涨跌幅': stock_data['涨跌幅'].values[0],
                    '成交量': stock_data['成交量'].values[0],
                    '成交额': stock_data['成交额'].values[0],
                    '振幅': stock_data['振幅'].values[0],
                    '最高': stock_data['最高'].values[0],
                    '最低': stock_data['最低'].values[0],
                    '今开': stock_data['今开'].values[0],
                    '昨收': stock_data['昨收'].values[0],
                    '换手率': stock_data['换手率'].values[0],
                    '市盈率-动态': stock_data['市盈率-动态'].values[0],
                    '市净率': stock_data['市净率'].values[0],
                    '总市值': stock_data['总市值'].values[0],
                    '流通市值': stock_data['流通市值'].values[0],
                    '涨速': stock_data['涨速'].values[0],
                    '5分钟涨跌': stock_data['5分钟涨跌'].values[0],
                    '60日涨跌幅': stock_data['60日涨跌幅'].values[0],
                    '年初至今涨跌幅': stock_data['年初至今涨跌幅'].values[0]
                }
                stock_list.append(stock_info)
        except Exception as e:
            print(f"处理 {code} 时出错: {e}")
            continue
    
    print(f"成功获取 {len(stock_list)} 只股票数据")
    return pd.DataFrame(stock_list)


def filter_stocks(df):
    """根据筛选条件筛选股票"""
    print("\n正在筛选符合条件的股票...")
    
    # 筛选条件：至少满足3条
    conditions = []
    
    # 市盈率（PE）小于30
    condition_pe = (df['市盈率-动态'] < 30) & (df['市盈率-动态'] > 0)
    conditions.append(condition_pe)
    
    # 市净率（PB）小于3
    condition_pb = (df['市净率'] < 3) & (df['市净率'] > 0)
    conditions.append(condition_pb)
    
    # 今日涨幅大于0
    condition_up = df['涨跌幅'] > 0
    conditions.append(condition_up)
    
    # 换手率大于1%
    condition_turnover = df['换手率'] > 1
    conditions.append(condition_turnover)
    
    # 流通市值在100亿-1000亿之间
    condition_cap = (df['流通市值'] > 10000000000) & (df['流通市值'] < 1000000000000)
    conditions.append(condition_cap)
    
    # 股价低于20元
    condition_price = df['最新价'] < 20
    conditions.append(condition_price)
    
    # 计算每只股票满足的条件数量
    df['满足条件数'] = sum(cond.astype(int) for cond in conditions)
    
    # 筛选满足至少3个条件的股票
    filtered_df = df[df['满足条件数'] >= 3].copy()
    
    # 计算综合评分（简单的加权评分）
    filtered_df['综合评分'] = (
        (30 - filtered_df['市盈率-动态'].clip(0, 30)) * 0.2 +
        (3 - filtered_df['市净率'].clip(0, 3)) * 0.2 +
        filtered_df['涨跌幅'].clip(0, 10) * 0.15 +
        filtered_df['换手率'].clip(0, 20) * 0.15 +
        (1000000000000 - filtered_df['流通市值']) / 100000000000 * 0.15 +
        (20 - filtered_df['最新价'].clip(0, 20)) * 0.15
    )
    
    # 按综合评分排序
    filtered_df = filtered_df.sort_values('综合评分', ascending=False)
    
    print(f"筛选出 {len(filtered_df)} 只符合条件的股票")
    return filtered_df


def generate_report(filtered_df, output_file):
    """生成推荐报告"""
    print(f"\n正在生成推荐报告: {output_file}")
    
    date_str = datetime.now().strftime("%Y年%m月%d日")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("A股市场分析与沪深300成分股买入机会推荐报告\n")
        f.write("="*80 + "\n\n")
        f.write(f"报告生成时间: {date_str}\n\n")
        
        f.write("-"*80 + "\n")
        f.write("一、符合条件的股票列表（按综合评分排序）\n")
        f.write("-"*80 + "\n\n")
        
        if len(filtered_df) == 0:
            f.write("暂无符合条件的股票\n\n")
        else:
            for idx, row in filtered_df.iterrows():
                f.write(f"排名 {filtered_df.index.get_loc(idx) + 1}: {row['名称']} ({row['代码']})\n")
                f.write(f"  综合评分: {row['综合评分']:.2f}\n")
                f.write(f"  满足条件数: {row['满足条件数']}个\n")
                f.write(f"  最新价: {row['最新价']:.2f}元\n")
                f.write(f"  涨跌幅: {row['涨跌幅']:.2f}%\n")
                f.write(f"  市盈率(动态): {row['市盈率-动态']:.2f}\n")
                f.write(f"  市净率: {row['市净率']:.2f}\n")
                f.write(f"  换手率: {row['换手率']:.2f}%\n")
                f.write(f"  流通市值: {row['流通市值']/100000000:.2f}亿元\n\n")
        
        f.write("-"*80 + "\n")
        f.write("二、风险提示\n")
        f.write("-"*80 + "\n\n")
        f.write("1. 本报告基于历史数据和简单筛选条件生成，不构成任何投资建议。\n")
        f.write("2. 股市有风险，投资需谨慎。请投资者根据自身情况做出投资决策。\n")
        f.write("3. 市场情况随时变化，本报告数据仅反映当前时点的情况。\n")
        f.write("4. 建议投资者结合更多分析方法和信息进行综合判断。\n")
        f.write("5. 过往业绩不代表未来表现。\n\n")
        
        f.write("="*80 + "\n")
        f.write("报告结束\n")
        f.write("="*80 + "\n")
    
    print("报告生成完成！")


def main():
    # 1. 获取沪深300成分股
    hs300_df = get_hs300_constituents()
    stock_codes = hs300_df['品种代码'].tolist()
    
    # 2. 获取个股实时行情数据
    stock_data_df = get_batch_stock_data(stock_codes)
    
    if stock_data_df.empty:
        print("未获取到任何股票数据")
        return
    
    # 3. 筛选股票
    filtered_df = filter_stocks(stock_data_df)
    
    # 4. 生成报告
    today = datetime.now().strftime("%Y%m%d")
    output_file = f"/workspace/a_stock_recommendation_{today}.txt"
    generate_report(filtered_df, output_file)


if __name__ == "__main__":
    main()
