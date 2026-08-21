"""阶段 5（M6）会员闭环端到端冒烟测试。

覆盖：注册 → 登录 → /members/me；登录后下单关联会员（/orders/me 可见）；
登录后投递 → /public/jobs/applications/me 可见。
"""
import random

LOGIN_URL = "/api/v1/members/login"
REGISTER_URL = "/api/v1/members/register"


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _fresh_phone() -> str:
    return f"139{random.randint(10000000, 99999999)}"  # 11 位纯数字手机号


def test_member_register_login_and_me(client):
    phone = _fresh_phone()
    r = client.post(REGISTER_URL, json={"phone": phone, "password": "member123", "nickname": "测试会员"})
    assert r.status_code == 200, r.text

    r = client.post(LOGIN_URL, json={"phone": phone, "password": "member123"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["access_token"]
    assert data["member"]["phone"] == phone

    r = client.get("/api/v1/members/me", headers=_auth(data["access_token"]))
    assert r.status_code == 200, r.text
    assert r.json()["data"]["nickname"] == "测试会员"


def test_member_order_flow(client):
    """登录会员下单 → 订单关联 user_id → /orders/me 可见。"""
    phone = _fresh_phone()
    client.post(REGISTER_URL, json={"phone": phone, "password": "member123"})
    token = client.post(LOGIN_URL, json={"phone": phone, "password": "member123"}).json()["data"]["access_token"]

    payload = {
        "items": [{"product_id": 1, "quantity": 1}],
        "receiver_name": "张三",
        "receiver_phone": phone,
        "receiver_address": "广东省广州市天河区珠江新城 88 号",
        "remark": "M6 会员下单测试",
    }
    r = client.post("/api/v1/orders", json=payload, headers=_auth(token))
    assert r.status_code == 200, r.text
    order_no = r.json()["data"]["order_no"]

    r = client.get("/api/v1/orders/me", headers=_auth(token))
    assert r.status_code == 200, r.text
    items = r.json()["data"]["items"]
    assert any(o["order_no"] == order_no for o in items), r.text


def test_member_job_application_flow(client):
    """登录会员投递 → user_id 关联 → /public/jobs/applications/me 可见。"""
    phone = _fresh_phone()
    client.post(REGISTER_URL, json={"phone": phone, "password": "member123"})
    token = client.post(LOGIN_URL, json={"phone": phone, "password": "member123"}).json()["data"]["access_token"]

    jobs = client.get("/api/v1/public/jobs").json()["data"]["items"]
    assert jobs, "种子应有岗位"
    job_id = jobs[0]["id"]

    r = client.post(
        "/api/v1/public/jobs/apply",
        json={"job_id": job_id, "name": "测试投递", "phone": phone},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text

    r = client.get("/api/v1/public/jobs/applications/me", headers=_auth(token))
    assert r.status_code == 200, r.text
    assert any(a["job_id"] == job_id for a in r.json()["data"]["items"]), r.text


def test_anonymous_order_not_in_my_orders(client):
    """游客下单不关联会员：该会员的 /orders/me 不应包含游客订单。"""
    phone = _fresh_phone()
    client.post(REGISTER_URL, json={"phone": phone, "password": "member123"})
    token = client.post(LOGIN_URL, json={"phone": phone, "password": "member123"}).json()["data"]["access_token"]

    # 游客下单
    payload = {
        "items": [{"product_id": 1, "quantity": 1}],
        "receiver_name": "游客",
        "receiver_phone": _fresh_phone(),
        "receiver_address": "广东省佛山市顺德区 1 号",
    }
    r = client.post("/api/v1/orders", json=payload)
    assert r.status_code == 200, r.text
    guest_order_no = r.json()["data"]["order_no"]

    mine = client.get("/api/v1/orders/me", headers=_auth(token)).json()["data"]["items"]
    assert all(o["order_no"] != guest_order_no for o in mine)
