"""FastAPI 依赖：DB session + 当前用户鉴权 + RBAC。"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db as _get_db
from app.models.admin_user import AdminUser
from app.models.permission import Permission
from app.models.role_permission import RolePermission

# tokenUrl 仅用于 Swagger UI 的 Authorize 按钮
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login", auto_error=False)


def get_db() -> Session:
    """DB session 依赖。"""
    yield from _get_db()


def get_current_admin(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> "AdminUser":
    """从 Bearer token 解析当前后台管理员。

    Raises:
        HTTPException 401: 未带 token / token 无效 / token 过期
    """
    from app.models.admin_user import AdminUser  # 延迟导入避免循环

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供访问凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="无效的 token")
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    admin = db.get(AdminUser, int(sub))
    if admin is None or not admin.is_activate:
        raise HTTPException(status_code=401, detail="账号不存在或已禁用")
    return admin


def get_current_active_admin(
    admin: Annotated["AdminUser", Depends(get_current_admin)],
) -> "AdminUser":
    """要求管理员处于激活状态。"""
    if not admin.is_activate:
        raise HTTPException(status_code=403, detail="账号已禁用")
    return admin


def get_current_member(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> "User":
    """从 Bearer token 解析当前前台会员（role=member）。"""
    from app.models.user import User  # 延迟导入避免循环

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供访问凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub or payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="无效的 token")
    except JWTError:
        raise HTTPException(status_code=401, detail="token 无效或已过期")

    user = db.get(User, int(sub))
    if user is None or user.is_deleted or user.is_activate != 1:
        raise HTTPException(status_code=401, detail="账号不存在或已禁用")
    return user


def get_optional_member(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> "User | None":
    """可选当前会员：无 token / token 无效 / 账号失效 → None（供游客可访问的接口关联会员）。"""
    from app.models.user import User  # 延迟导入避免循环

    if not token:
        return None
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub or payload.get("type") != "access":
            return None
    except JWTError:
        return None
    user = db.get(User, int(sub))
    if user is None or user.is_deleted or user.is_activate != 1:
        return None
    return user


def _load_admin_permissions(admin: AdminUser, db: Session) -> set[str]:
    """取管理员权限代码集合（按 role_id 关联 role_permissions → permissions）。

    结果缓存在 admin 实例的 ``_perm_codes`` 上，避免同一请求内多次查询。
    """
    cached = getattr(admin, "_perm_codes", None)
    if cached is not None:
        return cached
    if not admin.role_id:
        admin._perm_codes = set()
        return admin._perm_codes
    rows = db.execute(
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .where(
            RolePermission.role_id == admin.role_id,
            RolePermission.is_activate == 1,
            Permission.is_activate == 1,
        )
    ).scalars().all()
    codes = set(rows)
    admin._perm_codes = codes
    return codes


def require_permission(*codes: str, mode: str = "any"):
    """依赖工厂：校验当前管理员是否拥有指定权限点。

    - ``mode="any"``（默认）：拥有 ``codes`` 中任意一个即通过
    - ``mode="all"``：必须同时拥有全部 ``codes``

    无权限抛出 ``403``。admin / editor（在种子中被授予全部权限点）自然通过。
    用法::

        @router.post("/admin/products")
        def create_product(
            payload: ProductCreate,
            db: DbDep,
            admin: Annotated["AdminUser", Depends(require_permission("product.create"))],
        ):
            ...
    """

    def _dep(
        admin: Annotated[AdminUser, Depends(get_current_active_admin)],
        db: Annotated[Session, Depends(get_db)],
    ) -> AdminUser:
        perms = _load_admin_permissions(admin, db)
        ok = any(c in perms for c in codes) if mode == "any" else all(c in perms for c in codes)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，无法访问该功能",
            )
        return admin

    return _dep


# 类型别名
DbDep = Annotated[Session, Depends(get_db)]
CurrentAdmin = Annotated["AdminUser", Depends(get_current_active_admin)]
CurrentMember = Annotated["User", Depends(get_current_member)]

__all__ = [
    "get_db",
    "get_current_admin",
    "get_current_active_admin",
    "get_current_member",
    "get_optional_member",
    "require_permission",
    "DbDep",
    "CurrentAdmin",
    "CurrentMember",
]
