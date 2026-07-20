from pathlib import Path

import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    total_user = int(metric_map['用户数'])
    chn_num = int(metric_map['流失人数'])
    churn_ratio = chn_num / total_user
    avg_ord = metric_map['平均订单数']

    metrics = [
        {"label": "总用户数", "value": f"{total_user:,}", "note": "人"},
        {"label": "流失用户", "value": f"{chn_num:,}", "note": "人"},
        {"label": "总体流失率", "value": f"{churn_ratio:.2%}", "note": ""},
        {"label": "平均订单数", "value": f"{float(avg_ord):.2f}", "note": "单/人"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    top_segment = segment_df.sort_values(by="流失率", ascending=False).iloc[0]
    stage_name = top_segment["TenureGroup"]
    rate_val = top_segment["流失率"]
    insight = (
        f"流失率最高的生命周期阶段为{stage_name}，该分组流失率为{rate_val:.2%}；"
        "本结果仅为横截面分组相关分析，不能证明生命周期长短直接造成用户流失，存在其他干扰变量。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }