"""会员 Pydantic 模型（前台注册/登录/个人中心）。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class MemberRegisterIn(ORMBase):
    """前台会员注册。"""

    phone: str = Field(pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(min_length=6, max_length=64, description="密码（≥6 位）")
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = None


class MemberLoginIn(ORMBase):
    """前台会员登录（M2-2-B 简化：手机号+密码；生产可扩展 SMS 验证码）。"""

    phone: str
    password: str


class MemberOut(ORMBase):
    """会员公开信息（不返回 password_hash）。"""

    id: int
    phone: str
    nickname: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    gender: int | None = None
    created_date: datetime | None = None
    last_login_date: datetime | None = None


class MemberListItem(ORMBase):
    """后台会员列表项。"""

    id: int
    phone: str
    nickname: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    gender: int | None = None
    is_activate: int = 1
    created_date: datetime | None = None
    last_login_date: datetime | None = None


class MemberUpdateIn(ORMBase):
    """后台编辑会员：昵称、邮箱、性别（手机号/密码不允许后台改）。"""

    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=128)
    gender: int | None = Field(default=None, ge=0, le=2, description="0=未知/1=男/2=女")


class MemberCreateIn(ORMBase):
    """后台手动添加会员：手机号 + 初始密码 + 可选昵称/邮箱。"""

    phone: str = Field(pattern=r"^1[3-9]\d{9}$", description="手机号")
    password: str = Field(min_length=6, max_length=64, description="初始密码（≥6 位）")
    nickname: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=128)