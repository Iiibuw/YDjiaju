"""阶段 1（M1 后端骨架 + 鉴权 + RBAC）端到端冒烟测试。

覆盖：
- 图形验证码接口
- admin 登录 / /auth/me（role 代码 + 部门名解析）
- 登录防爆破锁定
- 权限点放行（admin 可建产品）
- 权限点拦截（product 角色建新闻 → 403；建产品 → 200）
"""
import uuid

from app.core.security import hash_password
from app.db import session as dbsession
from app.models.admin_user import AdminUser
from app.models.category import Category
from app.models.role import Role

LOGIN_URL = "/api/v1/auth/login"


def _first_category_id() -> int:
    """取一个合法分类（满足 chk_products_category_or_space：category_id 或 space_id 必填）。"""
    with dbsession.SessionLocal() as db:
        cat = db.query(Category).first()
        return cat.id if cat else 0


def _product_payload(name: str) -> dict:
    return {
        "name": name,
        "product_code": "TEST-" + uuid.uuid4().hex[:8],  # 唯一，避免跨用例冲突
        "min_price_cents": 500000,
        "max_price_cents": 500000,
        "category_id": _first_category_id(),
        "status": "draft",
        "is_top": 0,
        "sort": 0,
        "support_order": 0,
    }


def _login(client, username: str, password: str):
    """DEBUG 模式下用固定验证码 ABCD 登录。"""
    return client.post(
        LOGIN_URL,
        json={
            "username": username,
            "password": password,
            "captcha_id": "x" * 8,  # dev 码校验在查 store 之前，id 可为任意值
            "captcha_code": "ABCD",
        },
    )


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_captcha_returns_png(client):
    r = client.get("/api/v1/auth/captcha")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["captcha_id"]
    assert data["captcha_image"].startswith("data:image/png;base64,")
    assert data["expires_in"] == 300


def test_admin_login_and_me(client):
    r = _login(client, "admin", "admin123")
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["access_token"]
    assert data["role"] == "admin"
    assert data["real_name"] == "超级管理员"

    me = client.get("/api/v1/auth/me", headers=_auth(data["access_token"]))
    assert me.status_code == 200, me.text
    me_data = me.json()["data"]
    assert me_data["role"] == "admin"
    assert me_data["dept_name"] == "研发中心"
    assert me_data["data_scope"] == "ALL"


def test_login_wrong_password_locks(client):
    """连续 5 次错误后锁定（用不存在用户，避免污染 admin）。"""
    for _ in range(5):
        r = _login(client, "ghost_admin", "wrongpass")
        assert r.status_code == 400, r.text
    r = _login(client, "ghost_admin", "wrongpass")
    assert r.status_code == 429, r.text


def test_admin_can_create_product(client):
    token = _login(client, "admin", "admin123").json()["data"]["access_token"]
    r = client.post("/api/v1/admin/products", json=_product_payload("RBAC 测试·实木书桌"), headers=_auth(token))
    assert r.status_code == 200, r.text
    assert r.json()["data"]["name"] == "RBAC 测试·实木书桌"


def test_product_role_denied_news_create(client):
    """product 角色：无 news.* 权限 → 403；有 product.create → 200。"""
    with dbsession.SessionLocal() as db:
        existing = db.query(AdminUser).filter_by(username="prod_user_1").first()
        if existing is None:
            role = db.query(Role).filter_by(code="product").first()
            u = AdminUser(
                username="prod_user_1",
                password_hash=hash_password("prod123"),
                real_name="产品管理员",
                role_id=role.id if role else None,
                data_scope="ALL",  # 枚举仅 ALL/REGION/STORE/SELF
                is_activate=1,
            )
            db.add(u)
            db.commit()

    r = _login(client, "prod_user_1", "prod123")
    assert r.status_code == 200, r.text
    token = r.json()["data"]["access_token"]

    # 建新闻（product 角色无 news.create）→ 403
    r = client.post(
        "/api/v1/admin/news",
        json={"title": "越权测试资讯", "content": "<p>x</p>", "category": "company"},
        headers=_auth(token),
    )
    assert r.status_code == 403, r.text
    assert "权限不足" in r.json()["message"]

    # 建产品（product 角色有 product.create）→ 200
    r = client.post(
        "/api/v1/admin/products",
        json=_product_payload("越权测试产品"),
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
