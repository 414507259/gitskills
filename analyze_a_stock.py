import akshare as ak
import pandas as pd
from datetime import datetime

def get_csi300_components():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    df = ak.index_stock_cons(symbol="000300")
    return df

def get_stock_quotes():
    """获取A股实时行情数据（包含沪深300成分股）"""
    print("正在获取A股实时行情数据...")
    # 使用 akshare 的行情数据
    df = ak.stock_zh_a_spot_em()
    return df

def filter_stocks(df, csi300_codes):
    """筛选符合条件的股票"""
    print("正在筛选符合条件的股票...")
    
    # 先只保留沪深300成分股
    df_filter = df[df['代码'].isin(csi300_codes)].copy()
    
    # 打印列名用于调试
    print("可用列名:", df_filter.columns.tolist())
    
    # 清理数据类型
    def clean_float(x):
        if pd.isna(x):
            return 0.0
        try:
            return float(x)
        except:
            return 0.0
    
    # 映射列名（根据 akshare 的实际列名）
    df_filter['市盈率'] = df_filter['市盈率-动态'].apply(clean_float)
    df_filter['市净率'] = df_filter['市净率'].apply(clean_float)
    df_filter['今日涨跌幅'] = df_filter['涨跌幅'].apply(clean_float)
    df_filter['换手率'] = df_filter['换手率'].apply(clean_float)
    df_filter['流通市值'] = df_filter['流通市值'].apply(clean_float) / 100000000  # 转换为亿元
    df_filter['最新价'] = df_filter['最新价'].apply(clean_float)
    
    # 计算满足条件数
    conditions = []
    conditions.append((df_filter['市盈率'] < 30) & (df_filter['市盈率'] > 0))
    conditions.append((df_filter['市净率'] < 3) & (df_filter['市净率'] > 0))
    conditions.append(df_filter['今日涨跌幅'] > 0)
    conditions.append(df_filter['换手率'] > 1)
    conditions.append((df_filter['流通市值'] > 100) & (df_filter['流通市值'] < 1000))
    conditions.append(df_filter['最新价'] < 20)
    
    # 统计满足条件数
    df_filter['满足条件数'] = sum(conditions)
    
    # 至少满足3条
    df_selected = df_filter[df_filter['满足条件数'] >= 3].copy()
    
    # 计算综合评分 (简单评分: 低PE/PB加分，高涨幅/换手率加分，适中市值加分)
    def calculate_score(row):
        score = 0
        # 市盈率评分: 越低越好 (0-30)
        if 0 < row['市盈率'] < 30:
            score += (30 - row['市盈率']) / 30 * 30
        # 市净率评分: 越低越好 (0-3)
        if 0 < row['市净率'] < 3:
            score += (3 - row['市净率']) / 3 * 25
        # 涨跌幅评分: 越高越好 (0-10%)
        if row['今日涨跌幅'] > 0:
            score += min(row['今日涨跌幅'], 10) / 10 * 20
        # 换手率评分: 适中 (1-10%)
        if 1 < row['换手率'] < 10:
            score += 15
        # 流通市值评分: 适中 (100-1000亿)
        if 100 < row['流通市值'] < 1000:
            score += 10
        return round(score, 2)
    
    df_selected['综合评分'] = df_selected.apply(calculate_score, axis=1)
    
    # 按评分排序
    df_selected = df_selected.sort_values(by='综合评分', ascending=False)
    
    return df_selected

def generate_report(df_selected, date_str):
    """生成推荐报告"""
    print("正在生成推荐报告...")
    filename = f"/workspace/a_stock_recommendation_{date_str}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write(f"A股市场推荐报告 - {date_str}\n")
        f.write("="*60 + "\n\n")
        
        f.write("一、筛选条件说明\n")
        f.write("-"*60 + "\n")
        f.write("1. 市盈率（PE）小于30\n")
        f.write("2. 市净率（PB）小于3\n")
        f.write("3. 今日涨幅大于0\n")
        f.write("4. 换手率大于1%\n")
        f.write("5. 流通市值在100亿-1000亿之间\n")
        f.write("6. 股价低于20元\n")
        f.write(f"注：至少满足以上3条条件\n\n")
        
        f.write(f"二、符合条件的股票列表（共{len(df_selected)}只）\n")
        f.write("-"*60 + "\n\n")
        
        if len(df_selected) == 0:
            f.write("暂无符合条件的股票\n")
        else:
            for idx, (_, row) in enumerate(df_selected.iterrows(), 1):
                f.write(f"【{idx}】{row['名称']} ({row['代码']})\n")
                f.write(f"    综合评分: {row['综合评分']}\n")
                f.write(f"    满足条件数: {int(row['满足条件数'])}/6\n")
                f.write(f"    最新价: {row['最新价']:.2f} 元\n")
                f.write(f"    市盈率: {row['市盈率']:.2f}\n")
                f.write(f"    市净率: {row['市净率']:.2f}\n")
                f.write(f"    今日涨跌幅: {row['今日涨跌幅']:.2f}%\n")
                f.write(f"    换手率: {row['换手率']:.2f}%\n")
                f.write(f"    流通市值: {row['流通市值']:.2f} 亿元\n")
                f.write("\n")
        
        f.write("三、风险提示\n")
        f.write("-"*60 + "\n")
        f.write("1. 本报告基于历史数据和当前行情生成，不构成任何投资建议\n")
        f.write("2. 股市有风险，投资需谨慎\n")
        f.write("3. 请根据自身风险承受能力做出投资决策\n")
        f.write("4. 建议结合更多基本面和技术面分析进行判断\n\n")
        
        f.write("="*60 + "\n")
        f.write("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("="*60 + "\n")
    
    print(f"报告已生成: {filename}")
    return filename

def main():
    date_str = datetime.now().strftime("%Y%m%d")
    
    # 步骤1: 获取沪深300成分股
    csi300 = get_csi300_components()
    print(f"沪深300成分股数量: {len(csi300)}")
    csi300_codes = csi300['品种代码'].tolist()
    
    # 步骤2: 获取A股实时行情
    quotes_df = get_stock_quotes()
    print(f"获取到 {len(quotes_df)} 只股票的行情数据")
    
    # 步骤3: 筛选股票
    selected_df = filter_stocks(quotes_df, csi300_codes)
    
    # 步骤4: 生成报告
    generate_report(selected_df, date_str)

if __name__ == "__main__":
    main()
