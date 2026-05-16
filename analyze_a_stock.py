
import akshare as ak
import pandas as pd
from datetime import datetime


def get_csi300_components():
    """获取沪深300成分股列表"""
    try:
        df = ak.index_stock_cons(symbol="000300")
        return df
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return None


def get_stock_realtime_data(symbol):
    """获取个股实时行情数据"""
    try:
        df = ak.stock_individual_spot_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取股票 {symbol} 数据失败: {e}")
        return None


def get_csi300_realtime_quote():
    """获取沪深300成分股实时行情"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception as e:
        print(f"获取沪深A股实时行情失败: {e}")
        return None


def filter_stocks(df):
    """筛选符合条件的股票"""
    # 定义筛选条件
    conditions = []

    # 条件1: 市盈率 < 30
    df['pe_condition'] = df['市盈率-动态'] < 30
    conditions.append('pe_condition')

    # 条件2: 市净率 < 3
    df['pb_condition'] = df['市净率'] < 3
    conditions.append('pb_condition')

    # 条件3: 今日涨幅 > 0
    df['change_condition'] = df['涨跌幅'] > 0
    conditions.append('change_condition')

    # 条件4: 换手率 > 1%
    df['turnover_condition'] = df['换手率'] > 1
    conditions.append('turnover_condition')

    # 条件5: 流通市值在100亿-1000亿之间
    df['cap_condition'] = (df['流通市值'] > 10000000000) & (df['流通市值'] < 100000000000)
    conditions.append('cap_condition')

    # 条件6: 股价低于20元
    df['price_condition'] = df['最新价'] < 20
    conditions.append('price_condition')

    # 计算满足条件数量
    df['satisfied_conditions'] = df[conditions].sum(axis=1)

    # 筛选至少满足3个条件的股票
    filtered_df = df[df['satisfied_conditions'] >= 3].copy()

    # 计算综合评分（根据满足条件数量和其他指标）
    filtered_df['score'] = (
        filtered_df['satisfied_conditions'] * 10 +
        (30 - filtered_df['市盈率-动态'].clip(lower=0)).fillna(0) +
        (3 - filtered_df['市净率'].clip(lower=0)).fillna(0) +
        filtered_df['涨跌幅'].fillna(0)
    )

    # 按综合评分降序排序
    filtered_df = filtered_df.sort_values(by='score', ascending=False)

    return filtered_df


def generate_report(filtered_df, output_file):
    """生成推荐报告"""
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("A股市场推荐报告\n")
        f.write("=" * 80 + "\n")
        f.write(f"生成时间: {current_date}\n\n")

        # 筛选条件说明
        f.write("筛选条件（至少满足3条）：\n")
        f.write("1. 市盈率（PE）小于30\n")
        f.write("2. 市净率（PB）小于3\n")
        f.write("3. 今日涨幅大于0\n")
        f.write("4. 换手率大于1%\n")
        f.write("5. 流通市值在100亿-1000亿之间\n")
        f.write("6. 股价低于20元\n\n")

        f.write("-" * 80 + "\n")
        f.write(f"共找到 {len(filtered_df)} 只符合条件的股票\n")
        f.write("-" * 80 + "\n\n")

        # 股票列表
        for idx, row in filtered_df.iterrows():
            f.write(f"【{idx + 1}】 {row['名称']} ({row['代码']})\n")
            f.write(f"    最新价: {row['最新价']:.2f} 元\n")
            f.write(f"    涨跌幅: {row['涨跌幅']:.2f}%\n")
            f.write(f"    市盈率-动态: {row['市盈率-动态']:.2f}\n")
            f.write(f"    市净率: {row['市净率']:.2f}\n")
            f.write(f"    换手率: {row['换手率']:.2f}%\n")
            f.write(f"    流通市值: {row['流通市值'] / 100000000:.2f} 亿元\n")
            f.write(f"    满足条件数量: {int(row['satisfied_conditions'])}\n")

            # 列出满足的具体条件
            satisfied = []
            if row['pe_condition']:
                satisfied.append("PE&lt;30")
            if row['pb_condition']:
                satisfied.append("PB&lt;3")
            if row['change_condition']:
                satisfied.append("今日上涨")
            if row['turnover_condition']:
                satisfied.append("换手率&gt;1%")
            if row['cap_condition']:
                satisfied.append("流通市值100-1000亿")
            if row['price_condition']:
                satisfied.append("股价&lt;20元")
            f.write(f"    满足条件: {', '.join(satisfied)}\n\n")

        # 风险提示
        f.write("=" * 80 + "\n")
        f.write("风险提示\n")
        f.write("=" * 80 + "\n")
        f.write("1. 本报告仅供参考，不构成投资建议\n")
        f.write("2. 股市有风险，投资需谨慎\n")
        f.write("3. 过往业绩不代表未来表现\n")
        f.write("4. 请结合自身风险承受能力进行投资决策\n")

    print(f"推荐报告已生成: {output_file}")


def main():
    # 获取日期
    today = datetime.now().strftime("%Y%m%d")
    output_file = f"/workspace/a_stock_recommendation_{today}.txt"

    print("正在获取沪深A股实时行情数据...")
    df = get_csi300_realtime_quote()
    if df is None:
        print("获取行情数据失败")
        return

    # 获取沪深300成分股代码
    print("正在获取沪深300成分股...")
    csi300 = get_csi300_components()
    if csi300 is None:
        print("获取成分股失败")
        return

    # 筛选出沪深300成分股
    csi300_codes = set(csi300['品种代码'])
    df_csi300 = df[df['代码'].isin(csi300_codes)].copy()

    print(f"沪深300成分股数量: {len(df_csi300)}")

    # 筛选股票
    print("正在筛选符合条件的股票...")
    filtered_df = filter_stocks(df_csi300)

    # 生成报告
    generate_report(filtered_df, output_file)


if __name__ == "__main__":
    main()
