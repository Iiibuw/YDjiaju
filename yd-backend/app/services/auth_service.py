"""鉴权服务：图形验证码 + 登录 + 防爆破。

简化实现（M1）：
- 验证码存内存字典（生产应换 Redis）；4 字符，5 分钟过期
- 防爆破：连续 5 次错误锁定 15 分钟
"""
import base64
import time
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.captcha import generate_captcha_png
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.admin_user import AdminUser
from app.schemas.auth import CaptchaOut, LoginIn, TokenOut

# ⚠️ 内存存储：生产必须替换为 Redis
_captcha_store: dict[str, tuple[str, float]] = {}
_login_attempts: dict[str, tuple[int, float]] = {}


def _cleanup_captchas() -> None:
    now = time.time()
    expired = [k for k, (_, exp) in _captcha_store.items() if exp < now]
    for k in expired:
        _captcha_store.pop(k, None)


def new_captcha() -> CaptchaOut:
    """生成图形验证码 + 返回前端可用格式。"""
    _cleanup_captchas()
    text, png_bytes = generate_captcha_png()
    captcha_id = uuid.uuid4().hex
    expires_at = time.time() + settings.CAPTCHA_EXPIRE_SECONDS
    _captcha_store[captcha_id] = (text.upper(), expires_at)
    return CaptchaOut(
        captcha_id=captcha_id,
        captcha_image="data:image/png;base64," + base64.b64encode(png_bytes).decode(),
        expires_in=settings.CAPTCHA_EXPIRE_SECONDS,
    )


def verify_captcha(captcha_id: str, code: str) -> bool:
    """校验 captcha；成功立即删除 key（防重放）。"""
    info = _captcha_store.pop(captcha_id, None)
    if not info:
        return False
    text, expire_at = info
    if time.time() > expire_at:
        return False
    return text == code.upper().strip()


def _is_locked(username: str) -> tuple[bool, int]:
    info = _login_attempts.get(username)
    if not info:
        return False, 0
    failed, locked_until = info
    now = time.time()
    if locked_until > now:
        return True, int(locked_until - now) + 1
    return False, 0


def _record_failure(username: str) -> None:
    failed, _ = _login_attempts.get(username, (0, 0.0))
    failed += 1
    if failed >= settings.CAPTCHA_MAX_FAILED_ATTEMPTS:
        _login_attempts[username] = (failed, time.time() + settings.CAPTCHA_LOCK_MINUTES * 60)
    else:
        _login_attempts[username] = (failed, 0.0)


def _clear_failure(username: str) -> None:
    _login_attempts.pop(username, None)


def login(payload: LoginIn, db: Session) -> TokenOut:
    """登录主流程。"""
    locked, retry_after = _is_locked(payload.username)
    if locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多，请 {retry_after} 秒后重试",
        )

    if not verify_captcha(payload.captcha_id, payload.captcha_code):
        _record_failure(payload.username)
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    admin = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if not admin:
        _record_failure(payload.username)
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not verify_password(payload.password, admin.password_hash):
        _record_failure(payload.username)
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not admin.is_activate:
        raise HTTPException(status_code=403, detail="账号已禁用")

    from datetime import datetime

    admin.last_login_date = datetime.now()
    admin.failed_attempts = 0
    db.commit()

    _clear_failure(payload.username)

    extra = {"data_scope": admin.data_scope, "role": None}
    token = create_access_token(admin.id, extra)

    return TokenOut(
        access_token=token,
        token_type="Bearer",
        expires_in=settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
        admin_id=admin.id,
        real_name=admin.real_name,
        role=None,
        avatar_url=admin.avatar_url,
    )


def get_admin_profile(admin: AdminUser) -> dict:
    """组装 admin 个人资料。"""
    return {
        "id": admin.id,
        "username": admin.username,
        "real_name": admin.real_name,
        "nickname": admin.nickname,
        "avatar_url": admin.avatar_url,
        "role": None,  # TODO M2：关联 roles.code
        "dept_name": None,  # TODO M2：关联 depts.name
        "data_scope": admin.data_scope,
    }


__all__ = ["new_captcha", "login", "get_admin_profile"]
