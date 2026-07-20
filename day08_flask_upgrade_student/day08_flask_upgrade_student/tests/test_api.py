import json
from pathlib import Path
import pytest
from app import app, BASE_DIR

# 测试客户端固件
@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-key"
    with app.test_client() as test_client:
        yield test_client

# 场景1：测试 /health 接口返回200状态码
def test_health_api(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["ok"] is True
    assert "service" in data

# 场景2：未登录访问 /api/metrics 被登录拦截（302重定向到登录页）
def test_metrics_unlogin_block(client):
    resp = client.get("/api/metrics")
    # 未登录跳转登录页面，状态码302
    assert resp.status_code == 302
    assert "/login" in resp.location

# 场景3：登录后访问 /api/metrics，正常返回ok与metrics数组
def test_metrics_login_success(client):
    # 模拟登录
    client.post("/login", data={"username": "student", "password": "day07"})
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    res_data = json.loads(resp.data)
    assert res_data["ok"] is True
    assert isinstance(res_data["metrics"], list)
    # 校验指标字段齐全
    first_metric = res_data["metrics"][0]
    assert "label" in first_metric
    assert "value" in first_metric
    assert "note" in first_metric

# 场景4：登录后带category参数筛选品类接口
def test_categories_filter_fashion(client):
    # 登录
    client.post("/login", data={"username": "student", "password": "day07"})
    resp = client.get("/api/categories?category=Fashion")
    assert resp.status_code == 200
    res_data = json.loads(resp.data)
    assert res_data["ok"] is True
    assert res_data["category"] == "Fashion"
    assert isinstance(res_data["rows"], list)
    # 验证筛选生效，每条数据品类为Fashion
    for row in res_data["rows"]:
        assert row["偏好品类"] == "Fashion"