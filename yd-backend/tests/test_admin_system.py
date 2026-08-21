"""阶段 2（M3 系统域）冒烟测试。

覆盖：角色 CRUD + 授权、权限按模块分组、管理员 CRUD + 重置密码 + 禁用、内置角色/超管保护、
仪表盘统计、审计日志写入与查询、越权拦截（service 无 system.* → 403）。
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


def test_admin_roles_crud_and_grant(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/admin/roles",
        json={"name": "测试角色", "code": "tester", "data_scope": "ALL"},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
    role_id = r.json()["data"]["id"]

    perms = client.get("/api/v1/admin/permissions/flat", headers=_auth(token)).json()["data"]
    pid_product = next(p["id"] for p in perms if p["code"] == "product.view")
    pid_news = next(p["id"] for p in perms if p["code"] == "news.view")

    r = client.put(
        f"/api/v1/admin/roles/{role_id}/permissions",
        json={"permission_ids": [pid_product, pid_news]},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
    assert set(r.json()["data"]["permission_ids"]) == {pid_product, pid_news}, r.text

    r = client.get("/api/v1/admin/roles", headers=_auth(token))
    assert r.status_code == 200 and r.json()["data"]["total"] >= 6, r.text

    # 内置角色 admin 不可删
    admin_role = next(
        rr for rr in client.get("/api/v1/admin/roles", headers=_auth(token)).json()["data"]["items"] if rr["code"] == "admin"
    )
    r = client.delete(f"/api/v1/admin/roles/{admin_role['id']}", headers=_auth(token))
    assert r.status_code == 400, r.text


def test_admin_users_crud_password_and_disable(client):
    token = _admin_token(client)
    r = client.post(
        "/api/v1/admin/users",
        json={"username": "new_admin_1", "password": "newpass123", "real_name": "新管理员", "data_scope": "ALL"},
        headers=_auth(token),
    )
    assert r.status_code == 200, r.text
    user_id = r.json()["data"]["id"]

    assert _login(client, "new_admin_1", "newpass123").status_code == 200

    r = client.put(f"/api/v1/admin/users/{user_id}/password", json={"password": "reset456"}, headers=_auth(token))
    assert r.status_code == 200, r.text
    assert _login(client, "new_admin_1", "reset456").status_code == 200

    # 禁用后登录 → 403 账号已禁用
    r = client.put(f"/api/v1/admin/users/{user_id}", json={"is_activate": 0}, headers=_auth(token))
    assert r.status_code == 200, r.text
    assert _login(client, "new_admin_1", "reset456").status_code == 403

    # 删除
    r = client.delete(f"/api/v1/admin/users/{user_id}", headers=_auth(token))
    assert r.status_code == 200, r.text

    # 内置超管不可删
    admin_id = _login(client, "admin", "admin123").json()["data"]["admin_id"]
    r = client.delete(f"/api/v1/admin/users/{admin_id}", headers=_auth(token))
    assert r.status_code == 400, r.text


def test_dashboard_stats(client):
    token = _admin_token(client)
    r = client.get("/api/v1/admin/dashboard/stats", headers=_auth(token))
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["counts"]["members"] >= 2
    assert data["counts"]["products"] >= 1
    assert len(data["days"]) == 7
    assert len(data["orders"]) == 7 and len(data["visits"]) == 7


def test_audit_logs_recorded_and_queried(client):
    token = _admin_token(client)
    client.post(
        "/api/v1/admin/roles",
        json={"name": "审计测试", "code": "audit_test", "data_scope": "ALL"},
        headers=_auth(token),
    )
    r = client.get("/api/v1/admin/audit-logs", headers=_auth(token))
    assert r.status_code == 200, r.text
    items = r.json()["data"]["items"]
    assert any(a["action"] == "role.create" for a in items), r.text


def test_service_role_denied_system(client):
    """service 角色（无 system.* 权限）访问系统管理 → 403。"""
    with dbsession.SessionLocal() as db:
        if not db.query(AdminUser).filter_by(username="sys_user_1").first():
            role = db.query(Role).filter_by(code="service").first()
            db.add(
                AdminUser(
                    username="sys_user_1",
                    password_hash=hash_password("service123"),
                    real_name="客服用户",
                    role_id=role.id if role else None,
                    data_scope="REGION",
                    is_activate=1,
                )
            )
            db.commit()

    token = _login(client, "sys_user_1", "service123").json()["data"]["access_token"]
    r = client.get("/api/v1/admin/roles", headers=_auth(token))
    assert r.status_code == 403, r.text
    assert "权限不足" in r.json()["message"]
