import akshare as ak
import pandas as pd
import datetime

def get_csi300_stocks():
    try:
        csi300 = ak.index_stock_cons(symbol="000300")
        return csi300
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return None

def get_all_stock_data():
    data_sources = []
    
    try:
        df1 = ak.stock_zh_a_spot()
        if not df1.empty:
            data_sources.append(df1)
            print(f"数据源1: {len(df1)}条记录, 列: {df1.columns.tolist()}")
    except Exception as e:
        print(f"数据源1失败: {e}")
    
    try:
        df2 = ak.stock_zh_a_spot_em()
        if not df2.empty:
            data_sources.append(df2)
            print(f"数据源2: {len(df2)}条记录, 列: {df2.columns.tolist()}")
    except Exception as e:
        print(f"数据源2失败: {e}")
    
    if data_sources:
        merged = data_sources[0]
        for df in data_sources[1:]:
            merged = pd.merge(merged, df, on=['代码', '名称'], how='outer')
        return merged
    return None

def main():
    today = datetime.datetime.now().strftime("%Y%m%d")
    output_file = f"/workspace/a_stock_recommendation_{today}.txt"
    
    print("获取沪深300成分股列表...")
    csi300_stocks = get_csi300_stocks()
    if csi300_stocks is None:
        print("无法获取沪深300成分股列表")
        return
    
    csi300_codes = set(csi300_stocks['品种代码'].astype(str))
    print(f"沪深300成分股数量: {len(csi300_codes)}")
    
    print("获取实时行情数据...")
    all_stock_data = get_all_stock_data()
    if all_stock_data is None:
        print("无法获取行情数据")
        return
    
    filtered_stocks = all_stock_data[all_stock_data['代码'].astype(str).isin(csi300_codes)]
    print(f"筛选后沪深300股票数量: {len(filtered_stocks)}")
    
    available_cols = filtered_stocks.columns.tolist()
    print(f"可用字段: {available_cols}")
    
    recommendations = []
    for _, row in filtered_stocks.iterrows():
        code = str(row['代码'])
        name = row['名称']
        
        price = row.get('最新价', 0)
        change_pct = row.get('涨跌幅', 0)
        pe = row.get('市盈率', row.get('PE', row.get('pe', 0)))
        pb = row.get('市净率', row.get('PB', row.get('pb', 0)))
        turnover = row.get('换手率', row.get('turnover', 0))
        market_cap = row.get('流通市值', row.get('市值', row.get('market_cap', 0)))
        
        conditions_met = 0
        conditions_list = []
        
        if pe > 0 and pe < 30:
            conditions_met += 1
            conditions_list.append("PE<30")
        if pb > 0 and pb < 3:
            conditions_met += 1
            conditions_list.append("PB<3")
        if change_pct > 0:
            conditions_met += 1
            conditions_list.append("涨幅>0")
        if turnover > 1:
            conditions_met += 1
            conditions_list.append("换手率>1%")
        if market_cap > 0:
            if 100 <= market_cap <= 1000:
                conditions_met += 1
                conditions_list.append("市值100-1000亿")
        if price > 0 and price < 20:
            conditions_met += 1
            conditions_list.append("股价<20元")
        
        if conditions_met >= 3:
            recommendations.append({
                '代码': code,
                '名称': name,
                '市盈率': pe,
                '市净率': pb,
                '涨跌幅': change_pct,
                '换手率': turnover,
                '流通市值': market_cap,
                '最新价': price,
                '条件满足数': conditions_met,
                '满足条件': conditions_list
            })
    
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df = recommendations_df.sort_values(by='条件满足数', ascending=False).reset_index(drop=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("        A股沪深300成分股买入机会推荐报告\n")
        f.write("=" * 70 + "\n")
        f.write(f"生成日期: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
        f.write(f"沪深300成分股总数: {len(csi300_codes)}\n")
        f.write(f"筛选后股票数: {len(filtered_stocks)}\n")
        f.write(f"符合条件股票数: {len(recommendations_df)}\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("【筛选条件】\n")
        f.write("  - 市盈率（PE）< 30\n")
        f.write("  - 市净率（PB）< 3\n")
        f.write("  - 今日涨幅 > 0\n")
        f.write("  - 换手率 > 1%\n")
        f.write("  - 流通市值: 100亿 - 1000亿\n")
        f.write("  - 股价 < 20元\n")
        f.write("  * 至少满足以上3条条件\n\n")
        
        f.write("【数据说明】\n")
        f.write(f"  本次分析可用字段: {', '.join(available_cols)}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("【推荐股票列表】（按条件满足数排序）\n")
        f.write("=" * 70 + "\n")
        
        if len(recommendations_df) == 0:
            f.write("  暂无符合条件的股票\n")
        else:
            for idx, row in recommendations_df.iterrows():
                f.write(f"\n--- 第{idx+1}位 ---\n")
                f.write(f"股票代码: {row['代码']}\n")
                f.write(f"股票名称: {row['名称']}\n")
                f.write(f"最新价格: {row['最新价']:.2f} 元\n")
                f.write(f"市盈率(PE): {row['市盈率']:.2f}\n")
                f.write(f"市净率(PB): {row['市净率']:.2f}\n")
                f.write(f"今日涨幅: {row['涨跌幅']:.2f}%\n")
                f.write(f"换手率: {row['换手率']:.2f}%\n")
                f.write(f"流通市值: {row['流通市值']:.2f} 亿\n")
                f.write(f"条件满足数: {row['条件满足数']}/6\n")
                f.write(f"满足条件: {', '.join(row['满足条件'])}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("【风险提示】\n")
        f.write("=" * 70 + "\n")
        f.write("1. 本报告仅基于历史数据和量化指标进行筛选，不构成投资建议\n")
        f.write("2. 股市有风险，投资需谨慎，建议投资者结合自身风险承受能力做出决策\n")
        f.write("3. 数据仅供参考，实际投资前请查阅最新市场数据和公司基本面信息\n")
        f.write("4. 股票价格受多种因素影响，过去表现不代表未来收益\n")
        f.write("5. 建议分散投资，避免过度集中持仓\n")
        f.write("=" * 70 + "\n")
    
    print(f"推荐报告已生成: {output_file}")

if __name__ == "__main__":
    main()