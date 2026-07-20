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
    metrics = [
        {"label": "总用户数", "value": f"{int(metric_map['用户数']):,}", "note": "人"},
        {"label": "流失用户", "value": f"{int(metric_map['流失人数']):,}", "note": "人"},
        {"label": "总体流失率", "value": f"{metric_map['流失率']:.1%}", "note": "用户占比"},
        {"label": "平均订单数", "value": f"{metric_map['平均订单数']:.2f}", "note": "单/人"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()
    if selected_category != "全部" and selected_category in categories:
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

    highest_risk = segment_df.loc[segment_df["流失率"].idxmax()]
    insight = (
        f"{highest_risk['TenureGroup']}的流失率最高，为{highest_risk['流失率']:.1%}。"
        "这是一项描述性观察，不能直接解释流失原因。"
    )

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
    }


def load_metric_api_data(base_dir: Path) -> list[dict]:
    """返回给JSON接口使用的指标卡数据。"""
    data = load_dashboard_data(base_dir)
    # 任务4要求：禁止直接传入DataFrame给jsonify，必须转成原生list/dict
    # data["metrics"] 已经是纯Python列表+字典，无pandas对象，可直接返回
    serializable_metrics = []
    for item in data["metrics"]:
        # 强制校验所有value为字符串/数字原生类型，杜绝pandas数值类型
        serializable_item = {
            "label": str(item["label"]),
            "value": str(item["value"]),
            "note": str(item["note"])
        }
        serializable_metrics.append(serializable_item)
    return serializable_metrics


def load_category_api_data(base_dir: Path, selected_category: str = "全部") -> list[dict]:
    """返回给JSON接口使用的筛选表格数据。"""
    data = load_dashboard_data(base_dir, selected_category)
    # data["category_rows"] 由 df.to_dict("records") 生成，是纯Python字典列表，无DataFrame
    return data["category_rows"]