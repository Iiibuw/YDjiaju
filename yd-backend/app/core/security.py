"""安全工具：JWT 签发/校验 + bcrypt 密码哈希。"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def _truncate(plain: str) -> bytes:
    """bcrypt 限制 72 字节，长密码截断。"""
    return plain.encode("utf-8")[:72]


def hash_password(plain: str) -> str:
    """bcrypt 哈希（默认 cost=12）。"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(_truncate(plain), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文与哈希。"""
    try:
        return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    """签发 access token。
    - subject: 通常是 admin_id / user_id
    - extra: 可附 claims（如 role、data_scope）
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """解码并校验 token，失败抛 JWTError。"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


__all__ = [
    "JWTError",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
]
