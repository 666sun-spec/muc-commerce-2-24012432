from pathlib import Path

import pandas as pd


def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    normalized = question.replace(" ", "").lower()

    # 定义返回结果变量，避免提前return终止函数
    reply = None

    # 1. 流失率相关问答
    if any(word in normalized for word in ["流失率", "流失", "流失人数"]):
        reply = f"平台总流失用户{int(metrics['流失人数']):,}人，流失率为{metrics['流失率']:.1%}。"
    # 2. 订单相关问答
    if any(word in normalized for word in ["订单", "平均订单", "单均"]):
        reply = f"平台人均平均订单数为{metrics['平均订单数']:.2f}单/人。"
    # 3. 生命周期风险问答（读取分段数据找最高流失阶段）
    if any(word in normalized for word in ["生命周期", "风险", "流失最高阶段"]):
        segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")
        segment_df.columns = segment_df.columns.str.strip()
        max_row = segment_df.loc[segment_df["流失率"].idxmax()]
        stage = max_row["TenureGroup"]
        rate = max_row["流失率"]
        reply = f"用户生命周期风险结论：{stage}阶段流失风险最高，流失率{rate:.1%}，是重点留存运营阶段。"
    # 4. 偏好品类问答（取全品类用户总数）
    if any(word in normalized for word in ["品类", "偏好", "商品分类"]):
        category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
        top_cat = category_df.loc[category_df["用户数"].idxmax(), "PreferedOrderCat"]
        reply = f"用户偏好品类结论：{top_cat}是用户选择最多的偏好品类，对应平台整体流失率{metrics['流失率']:.1%}。"


    if reply is not None:
        return reply
    return (
        "基础问答尚未完成。目前只能回答总用户数等。"
        "请换一种更具体的问法。"
    )