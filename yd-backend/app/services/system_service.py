"""系统管理服务层：角色 / 权限 / 管理员。"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.admin_user import AdminUser
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.schemas.system import AdminUserIn, AdminUserOut, AdminUserUpdate, RoleIn, RoleOut

# 内置角色代码，禁止删除/改 code
BUILTIN_ROLES = {"admin", "editor"}


def _role_out(db: Session, r: Role) -> RoleOut:
    out = RoleOut.model_validate(r)
    ids = db.execute(
        select(RolePermission.permission_id).where(RolePermission.role_id == r.id, RolePermission.is_activate == 1)
    ).scalars().all()
    out.permission_ids = list(ids)
    return out


# ===== 角色 =====

def list_roles(db: Session, *, keyword: str | None = None, page: int = 1, page_size: int = 50) -> tuple[list[RoleOut], int]:
    q = select(Role)
    if keyword:
        q = q.where(Role.name.like(f"%{keyword}%") | Role.code.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(Role.sort, Role.id).offset((page - 1) * page_size).limit(page_size)
    items = [_role_out(db, r) for r in db.execute(q).scalars().all()]
    return items, total


def create_role(db: Session, payload: RoleIn, admin_id: int) -> RoleOut:
    data: dict[str, Any] = payload.model_dump()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    r = Role(**data)
    db.add(r)
    db.commit()
    db.refresh(r)
    return _role_out(db, r)


def update_role(db: Session, role_id: int, payload: RoleIn, admin_id: int) -> RoleOut | None:
    r = db.get(Role, role_id)
    if not r:
        return None
    if r.code in BUILTIN_ROLES and payload.code != r.code:
        return None  # 内置角色禁止改 code
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    r.updated_at = admin_id
    db.commit()
    db.refresh(r)
    return _role_out(db, r)


def delete_role(db: Session, role_id: int, admin_id: int) -> bool:
    r = db.get(Role, role_id)
    if not r or r.code in BUILTIN_ROLES:
        return False
    # 有管理员使用该角色则拒绝
    used = db.scalar(select(func.count()).select_from(AdminUser).where(AdminUser.role_id == role_id))
    if used:
        return False
    db.delete(r)
    db.commit()
    return True


def set_role_permissions(db: Session, role_id: int, permission_ids: list[int], admin_id: int) -> RoleOut | None:
    """角色授权全量替换。"""
    r = db.get(Role, role_id)
    if not r:
        return None
    old = db.execute(select(RolePermission).where(RolePermission.role_id == role_id)).scalars().all()
    for o in old:
        o.is_activate = 0
        o.updated_at = admin_id
    for pid in permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=pid, is_activate=1, created_at=admin_id, updated_at=admin_id))
    db.commit()
    db.refresh(r)
    return _role_out(db, r)


# ===== 权限 =====

def list_permissions(db: Session, *, module: str | None = None) -> list[Permission]:
    q = select(Permission).where(Permission.is_activate == 1)
    if module:
        q = q.where(Permission.module == module)
    q = q.order_by(Permission.module, Permission.id)
    return list(db.execute(q).scalars().all())


def permission_modules(perms: list[Permission]) -> dict[str, list]:
    """按模块分组：{"product": [{id, code, name}, ...], ...}"""
    groups: dict[str, list] = {}
    for p in perms:
        groups.setdefault(p.module, []).append({"id": p.id, "code": p.code, "name": p.name})
    return groups


# ===== 管理员 =====

def _admin_out(db: Session, u: AdminUser) -> AdminUserOut:
    out = AdminUserOut.model_validate(u)
    if u.role_id:
        r = db.get(Role, u.role_id)
        out.role_code = r.code if r else None
    return out


def list_admin_users(db: Session, *, keyword: str | None = None, page: int = 1, page_size: int = 20) -> tuple[list[AdminUserOut], int]:
    q = select(AdminUser)
    if keyword:
        q = q.where(AdminUser.username.like(f"%{keyword}%") | AdminUser.real_name.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(AdminUser.id).offset((page - 1) * page_size).limit(page_size)
    items = [_admin_out(db, u) for u in db.execute(q).scalars().all()]
    return items, total


def create_admin_user(db: Session, payload: AdminUserIn, admin_id: int) -> AdminUserOut:
    data: dict[str, Any] = payload.model_dump()
    data["password_hash"] = hash_password(data.pop("password"))
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    u = AdminUser(**data)
    db.add(u)
    db.commit()
    db.refresh(u)
    return _admin_out(db, u)


def update_admin_user(db: Session, user_id: int, payload: AdminUserUpdate, admin_id: int) -> AdminUserOut | None:
    u = db.get(AdminUser, user_id)
    if not u:
        return None
    if u.username == "admin":
        return None  # 内置超管禁止编辑
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(u, k, v)
    u.updated_at = admin_id
    db.commit()
    db.refresh(u)
    return _admin_out(db, u)


def reset_password(db: Session, user_id: int, password: str, admin_id: int) -> bool:
    u = db.get(AdminUser, user_id)
    if not u:
        return False
    u.password_hash = hash_password(password)
    u.updated_at = admin_id
    db.commit()
    return True


def delete_admin_user(db: Session, user_id: int, admin_id: int) -> bool:
    u = db.get(AdminUser, user_id)
    if not u or u.username == "admin" or u.id == admin_id:
        return False
    db.delete(u)
    db.commit()
    return True


__all__ = [
    "list_roles", "create_role", "update_role", "delete_role", "set_role_permissions",
    "list_permissions", "permission_modules",
    "list_admin_users", "create_admin_user", "update_admin_user", "reset_password", "delete_admin_user",
]
