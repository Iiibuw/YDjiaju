"""FastAPI 依赖：DB session + 当前用户鉴权 + RBAC。"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db as _get_db

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


# 类型别名
DbDep = Annotated[Session, Depends(get_db)]
CurrentAdmin = Annotated["AdminUser", Depends(get_current_active_admin)]
CurrentMember = Annotated["User", Depends(get_current_member)]
