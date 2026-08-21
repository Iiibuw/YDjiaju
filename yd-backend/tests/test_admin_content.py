"""阶段 2（M2 内容域）后台模块冒烟测试。

覆盖：分类树 CRUD、轮播 CRUD、站点配置 upsert、角色权限拦截（product 无 download 权限 403、
有 banner 权限 200 —— 对齐原型 ROLES 校准）。
"""
from app.core.security import hash_password
from app.db import session as dbsession
from app.models.admin_user import AdminUser
from app.models.role import Role

LOGIN_URL = "/api/v1/auth/login"


def _login(client, username: str, password: str):
    return client.post(
        LOGIN_URL,
        json={"username": username, "password": password, "captcha_id": "x" * 8, "captcha_code": "ABCD"},
    )


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _admin_token(client) -> str:
    return _login(client, "admin", "admin123").json()["data"]["access_token"]


def test_admin_category_tree_crud(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/admin/categories",
        json={"kind": "category", "name": "实木餐桌", "sort": 1},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
    parent_id = r.json()["data"]["id"]

    r = client.post(
        "/api/v1/admin/categories",
        json={"kind": "category", "name": "1.8m 圆桌", "parent_id": parent_id},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text

    r = client.get("/api/v1/admin/categories", headers=_auth(token))
    assert r.status_code == 200, r.text
    tree = r.json()["data"]
    assert any(c["name"] == "实木餐桌" and c["children"] for c in tree)

    # 有子分类不可删 → 400
    r = client.delete(f"/api/v1/admin/categories/{parent_id}", headers=_auth(token))
    assert r.status_code == 400, r.text


def test_admin_banner_crud(client):
    token = _admin_token(client)
    payload = {"title": "胡桃禮首屏", "image_url": "https://example.com/a.png", "link_type": "product", "link_target": "1"}
    r = client.post("/api/v1/admin/banners", json=payload, headers=_auth(token))
    assert r.status_code == 200, r.text
    banner_id = r.json()["data"]["id"]

    r = client.get("/api/v1/admin/banners", headers=_auth(token))
    assert r.status_code == 200 and r.json()["data"]["total"] >= 1, r.text

    r = client.put(
        f"/api/v1/admin/banners/{banner_id}",
        json={**payload, "title": "胡桃禮首屏V2", "sort": 2},
        headers=_auth(token),
    )
    assert r.status_code == 200 and r.json()["data"]["title"] == "胡桃禮首屏V2", r.text

    r = client.delete(f"/api/v1/admin/banners/{banner_id}", headers=_auth(token))
    assert r.status_code == 200, r.text


def test_admin_site_config_upsert(client):
    token = _admin_token(client)
    body = {"config_key": "site_name", "config_value": "YD家居", "value_type": "string", "category": "basic"}
    r = client.post("/api/v1/admin/site-configs", json=body, headers=_auth(token))
    assert r.status_code == 200, r.text

    # upsert 幂等：再次保存更新值
    r = client.post(
        "/api/v1/admin/site-configs",
        json={**body, "config_value": "YD家居官网"},
        headers=_auth(token),
    )
    assert r.status_code == 200 and r.json()["data"]["config_value"] == "YD家居官网", r.text

    r = client.get("/api/v1/admin/site-configs/key/site_name", headers=_auth(token))
    assert r.status_code == 200 and r.json()["data"]["config_value"] == "YD家居官网", r.text


def test_product_role_denied_download_but_allowed_banner(client):
    """角色授权校准验证：product 无 download 权限（403），有 banner 权限（200，对齐原型 carousel）。"""
    with dbsession.SessionLocal() as db:
        if not db.query(AdminUser).filter_by(username="prod_user_2").first():
            role = db.query(Role).filter_by(code="product").first()
            db.add(
                AdminUser(
                    username="prod_user_2",
                    password_hash=hash_password("prod123"),
                    real_name="产品管理员2",
                    role_id=role.id if role else None,
                    data_scope="ALL",
                    is_activate=1,
                )
            )
            db.commit()

    token = _login(client, "prod_user_2", "prod123").json()["data"]["access_token"]

    r = client.post(
        "/api/v1/admin/downloads",
        json={"title": "越权下载", "file_url": "https://x/y.pdf"},
        headers=_auth(token),
    )
    assert r.status_code == 403, r.text
    assert "权限不足" in r.json()["message"]

    r = client.post(
        "/api/v1/admin/banners",
        json={"title": "越权轮播", "image_url": "https://x/b.png"},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
