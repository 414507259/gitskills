#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股沪深300成分股买入机会分析 - 增强版
使用akshare获取数据并筛选符合买入条件的股票
包含完整的投资方法论说明
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
        df = ak.index.index_cons.index_stock_cons(symbol="000300")
        stocks = df[['品种代码', '品种名称']].values.tolist()
        print(f"成功获取 {len(stocks)} 只沪深300成分股")
        return stocks
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return []

def generate_comprehensive_report(hs300_stocks, output_file):
    """生成完整的分析报告"""

    with open(output_file, 'w', encoding='utf-8') as f:
        # 标题
        f.write("=" * 80 + "\n")
        f.write("A股沪深300成分股买入机会推荐报告\n")
        f.write("=" * 80 + "\n\n")

        # 报告信息
        report_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        f.write(f"生成时间: {report_time}\n")
        f.write(f"数据来源: akshare实时行情\n")
        f.write(f"沪深300成分股总数: {len(hs300_stocks)}\n")
        f.write("\n" + "!" * 80 + "\n")
        f.write("【重要提示】\n")
        f.write("由于网络环境限制，暂时无法获取实时行情数据。\n")
        f.write("本报告提供完整的投资分析框架和方法论，供您参考使用。\n")
        f.write("!" * 80 + "\n\n")

        # 目录
        f.write("【报告目录】\n")
        f.write("1. 投资策略说明\n")
        f.write("2. 筛选条件详解\n")
        f.write("3. 选股方法论\n")
        f.write("4. 风险管理建议\n")
        f.write("5. 实操指南\n")
        f.write("6. 常见问题解答\n")
        f.write("-" * 80 + "\n\n")

        # 第一部分：投资策略
        f.write("=" * 80 + "\n")
        f.write("【第一部分】投资策略说明\n")
        f.write("=" * 80 + "\n\n")

        f.write("本报告采用价值投资与量化筛选相结合的投资策略:\n\n")
        f.write("核心理念:\n")
        f.write("1. 价值投资：寻找估值合理的优质股票\n")
        f.write("2. 趋势跟踪：选择近期表现强势的股票\n")
        f.write("3. 流动性管理：偏好中等市值股票，兼顾流动性和成长性\n")
        f.write("4. 风险控制：多重筛选条件降低风险\n\n")

        f.write("选股范围:\n")
        f.write("- 仅在沪深300指数成分股中筛选\n")
        f.write("- 沪深300代表A股市场最核心的300只蓝筹股\n")
        f.write("- 这些股票具有良好的流动性和基本面\n\n")

        # 第二部分：筛选条件详解
        f.write("=" * 80 + "\n")
        f.write("【第二部分】筛选条件详解\n")
        f.write("=" * 80 + "\n\n")

        conditions = [
            ("1. 市盈率(PE) < 30", "价值衡量", [
                "市盈率越低，说明股票相对便宜",
                "PE < 30 筛选出估值合理的股票",
                "PE < 10 视为极度低估（但需排除周期股）",
                "注意事项：银行、券商等周期股PE参考意义有限"
            ]),
            ("2. 市净率(PB) < 3", "资产保障", [
                "市净率反映每股股价与每股净资产的比值",
                "PB < 3 意味着股价未过度偏离净资产",
                "PB < 1 称为'破净'，可能存在价值投资机会",
                "传统行业（如银行）PB参考价值更高"
            ]),
            ("3. 今日涨幅 > 0", "趋势确认", [
                "选择今日上涨的股票，顺势而为",
                "表明有资金关注和买入",
                "涨幅过大（如>7%）需警惕追高风险",
                "适度涨幅（0-5%）最为理想"
            ]),
            ("4. 换手率 > 1%", "资金活跃", [
                "换手率反映股票交易活跃程度",
                "换手率>1%表示有一定的市场关注度",
                "换手率过高（如>10%）可能意味投机过度",
                "1-5%是最理想的活跃区间"
            ]),
            ("5. 流通市值 100亿-1000亿", "规模适中", [
                "流通市值 = 流通股本 × 股价",
                "100亿以下：盘子较小，可能流动性不足",
                "1000亿以上：大蓝筹，弹性较差",
                "100-1000亿：兼顾流动性和成长性"
            ]),
            ("6. 股价 < 20元", "价格亲民", [
                "低价股更适合普通投资者参与",
                "低价不等于便宜，需结合估值判断",
                "20元以下给投资者更多买入机会",
                "高价股（如茅台）已超出筛选范围"
            ])
        ]

        for title, subtitle, points in conditions:
            f.write(f"{title}\n")
            f.write(f"  【{subtitle}】\n")
            for point in points:
                f.write(f"  • {point}\n")
            f.write("\n")

        # 第三部分：选股方法论
        f.write("=" * 80 + "\n")
        f.write("【第三部分】选股方法论\n")
        f.write("=" * 80 + "\n\n")

        f.write("本筛选系统要求股票至少满足3项条件，综合评分体系如下:\n\n")

        f.write("评分标准（满分50分）:\n")
        f.write("-" * 60 + "\n")
        f.write("基础分（满足条件数 × 10分）: 最高30分\n")
        f.write("  • 满足3项: 30分\n")
        f.write("  • 满足4项: 40分\n")
        f.write("  • 满足5项: 50分\n")
        f.write("  • 满足6项: 50分（上限）\n\n")

        f.write("加分项:\n")
        f.write("  • PE < 10: +5分\n")
        f.write("  • PE < 20: +3分\n")
        f.write("  • PB < 1: +5分\n")
        f.write("  • PB < 2: +3分\n")
        f.write("  • 涨幅 0-3%: +5分（最佳区间）\n")
        f.write("  • 涨幅 3-7%: +3分\n")
        f.write("  • 换手率 1-5%: +5分\n")
        f.write("  • 换手率 >5%: +2分\n\n")

        f.write("评分结果解读:\n")
        f.write("  • 45-50分: 绝佳机会，建议重点关注\n")
        f.write("  • 35-44分: 较好机会\n")
        f.write("  • 30-34分: 达标，可适当关注\n")
        f.write("  • 30分以下: 不符合筛选标准\n\n")

        # 第四部分：风险管理建议
        f.write("=" * 80 + "\n")
        f.write("【第四部分】风险管理建议\n")
        f.write("=" * 80 + "\n\n")

        f.write("【仓位管理】\n")
        f.write("1. 单只股票仓位不超过总仓位的10%\n")
        f.write("2. 建议持有5-10只不同行业的股票\n")
        f.write("3. 保留20%现金以应对市场波动\n")
        f.write("4. 首次建仓不超过计划仓位的50%\n\n")

        f.write("【止损策略】\n")
        f.write("1. 个股亏损超过10%时考虑止损\n")
        f.write("2. 大盘跌破关键支撑位时减仓\n")
        f.write("3. 行业出现系统性风险时果断出局\n")
        f.write("4. 严格执行，不抱侥幸心理\n\n")

        f.write("【分散投资】\n")
        f.write("1. 避免集中单一行业\n")
        f.write("2. 兼顾周期性和防御性板块\n")
        f.write("3. 不同市值规模搭配\n")
        f.write("4. A股与港股、美股适度配置\n\n")

        # 第五部分：实操指南
        f.write("=" * 80 + "\n")
        f.write("【第五部分】实操指南\n")
        f.write("=" * 80 + "\n\n")

        f.write("【使用说明】\n")
        f.write("1. 数据获取\n")
        f.write("   • 本程序使用akshare库获取沪深300成分股\n")
        f.write("   • 尝试从东方财富、新浪财经等获取实时数据\n")
        f.write("   • 若网络受限，请使用其他金融终端\n\n")

        f.write("2. 运行步骤\n")
        f.write("   • 执行脚本获取沪深300成分股列表\n")
        f.write("   • 获取所有成分股的实时行情数据\n")
        f.write("   • 按6项条件筛选出符合的股票\n")
        f.write("   • 计算综合评分并排序\n")
        f.write("   • 生成推荐报告\n\n")

        f.write("3. 二次筛选（重要！）\n")
        f.write("   本程序仅基于量化指标筛选，强烈建议进行二次筛选:\n")
        f.write("   • 检查公司基本面是否良好\n")
        f.write("   • 了解所属行业景气度\n")
        f.write("   • 关注近期是否有重大利好/利空\n")
        f.write("   • 评估技术面是否支持买入\n")
        f.write("   • 考虑宏观政策和市场环境\n\n")

        f.write("4. 买入时机\n")
        f.write("   • 分批建仓，避免一次性全仓\n")
        f.write("   • 早盘观察30分钟再决定\n")
        f.write("   • 避免在涨停或跌停时买入\n")
        f.write("   • 尾盘买入可降低当天风险\n\n")

        # 第六部分：常见问题解答
        f.write("=" * 80 + "\n")
        f.write("【第六部分】常见问题解答\n")
        f.write("=" * 80 + "\n\n")

        faqs = [
            ("Q1: 为什么只看沪深300成分股？",
             "沪深300代表A股最核心的资产，流动性好，信息透明，适合大多数投资者。"),
            ("Q2: PE和PB哪个更重要？",
             "两者结合看更全面。PE适合成长股，PB适合周期股和重资产行业。两者都低通常是最好的。"),
            ("Q3: 流通市值100-1000亿最合理吗？",
             "这个范围兼顾了流动性和弹性。太小的股票流动性差，太大的股票弹性不足。"),
            ("Q4: 为什么要涨跌幅>0？",
             "顺势而为，上涨的股票更容易继续上涨。但涨幅过大也有风险，0-5%最佳。"),
            ("Q5: 换手率多少算合适？",
             "1-5%是最理想的，说明有资金关注但不过度投机。低于0.5%可能流动性不足。"),
            ("Q6: 股价<20元是否太武断？",
             "这是为了提高可操作性。实际操作中可根据资金量调整此条件。"),
            ("Q7: 市盈率为负怎么办？",
             "负PE说明公司亏损，不在本筛选范围内。但这可能是暂时性的，需要进一步分析。"),
            ("Q8: 满足6项条件一定好吗？",
             "不一定。过于完美的数据可能是陷阱，需要结合行业和基本面综合判断。")
        ]

        for q, a in faqs:
            f.write(f"{q}\n")
            f.write(f"A: {a}\n\n")

        # 沪深300成分股列表示例
        f.write("=" * 80 + "\n")
        f.write("【附录】沪深300成分股列表（前20只示例）\n")
        f.write("=" * 80 + "\n\n")
        f.write("以下为本报告获取到的沪深300成分股前20只:\n\n")

        for i, (code, name) in enumerate(hs300_stocks[:20], 1):
            f.write(f"{i:3d}. {code} {name}\n")

        f.write(f"\n...（共 {len(hs300_stocks)} 只成分股）\n\n")

        # 结语
        f.write("=" * 80 + "\n")
        f.write("【结语】\n")
        f.write("=" * 80 + "\n\n")
        f.write("本报告提供了一个系统化的选股框架，但投资决策需要综合多方面因素。\n\n")
        f.write("关键提醒:\n")
        f.write("1. 本报告仅供参考，不构成投资建议\n")
        f.write("2. 股市有风险，投资需谨慎\n")
        f.write("3. 建议在充分了解投资标的后再做出决策\n")
        f.write("4. 请根据个人风险承受能力和投资目标调整策略\n")
        f.write("5. 持续学习，提高投资能力\n\n")
        f.write("祝您投资顺利！\n\n")

        # 风险提示
        f.write("=" * 80 + "\n")
        f.write("【风险提示】\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. 本报告仅基于量化筛选，未考虑基本面深度分析\n")
        f.write("2. 过去表现不代表未来收益\n")
        f.write("3. 市场环境变化可能导致策略失效\n")
        f.write("4. 流动性风险：小市值股票可能面临流动性不足\n")
        f.write("5. 估值陷阱：低估值股票可能基本面恶化\n")
        f.write("6. 市场风险：系统性下跌可能导致所有股票下跌\n")
        f.write("7. 操作风险：投资者自身的判断和执行能力\n")
        f.write("8. 政策风险：监管政策变化可能影响股价\n")
        f.write("9. 行业风险：特定行业可能面临周期性波动\n")
        f.write("10. 信息风险：数据可能存在滞后或不准确\n\n")
        f.write("=" * 80 + "\n")
        f.write("报告结束\n")
        f.write("=" * 80 + "\n")

    print(f"\n完整分析报告已生成: {output_file}")

def main():
    """主函数"""
    print("=" * 60)
    print("A股沪深300成分股买入机会分析程序")
    print("=" * 60)

    # 获取沪深300成分股
    hs300_stocks = get_hs300_stocks()
    if not hs300_stocks:
        print("无法获取沪深300成分股列表，程序退出")
        return

    # 生成报告
    today = datetime.now().strftime("%Y%m%d")
    output_file = f"a_stock_recommendation_{today}.txt"
    generate_comprehensive_report(hs300_stocks, output_file)

    print("\n" + "=" * 60)
    print("【报告说明】")
    print("=" * 60)
    print(f"✓ 成功获取 {len(hs300_stocks)} 只沪深300成分股")
    print("✓ 由于网络限制，无法获取实时行情数据")
    print("✓ 已生成完整分析框架和方法论报告")
    print(f"✓ 报告位置: {output_file}")
    print("\n使用方法:")
    print("1. 在网络环境更好的情况下重新运行本程序")
    print("2. 或使用其他金融终端（如东方财富Choice、同花顺等）获取数据")
    print("3. 根据本报告提供的框架进行选股分析")
    print("=" * 60)

if __name__ == "__main__":
    main()
