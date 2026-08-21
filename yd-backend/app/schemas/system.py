"""系统管理 Pydantic 模型（角色 / 权限 / 管理员）。"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class RoleIn(BaseModel):
    """创建/更新角色。"""

    name: str = Field(min_length=1, max_length=64, description="角色名称")
    code: str = Field(min_length=1, max_length=32, description="角色代码（唯一）")
    description: str | None = Field(default=None, max_length=255)
    data_scope: str = Field(default="REGION", pattern="^(ALL|REGION|STORE|SELF)$", description="数据范围")
    sort: int = Field(default=0)
    is_activate: int = Field(default=1, ge=0, le=1)


class RoleOut(ORMBase):
    """角色列表项/详情。"""

    id: int
    name: str
    code: str
    description: str | None = None
    data_scope: str
    sort: int = 0
    is_activate: int = 1
    permission_ids: list[int] = Field(default_factory=list, description="已授权权限点 ID")


class RolePermIn(BaseModel):
    """角色授权（全量替换语义）。"""

    permission_ids: list[int] = Field(default_factory=list, description="权限点 ID 数组")


class PermissionOut(ORMBase):
    """权限点项。"""

    id: int
    name: str
    code: str
    module: str
    description: str | None = None


class AdminUserIn(BaseModel):
    """创建管理员。"""

    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    real_name: str | None = Field(default=None, max_length=64)
    nickname: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=128)
    dept_id: int | None = None
    role_id: int | None = None
    data_scope: str = Field(default="REGION", pattern="^(ALL|REGION|STORE|SELF)$")
    is_activate: int = Field(default=1, ge=0, le=1)


class AdminUserUpdate(BaseModel):
    """更新管理员（不含密码）。"""

    real_name: str | None = Field(default=None, max_length=64)
    nickname: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=128)
    dept_id: int | None = None
    role_id: int | None = None
    data_scope: str = Field(default="REGION", pattern="^(ALL|REGION|STORE|SELF)$")
    is_activate: int = Field(default=1, ge=0, le=1)


class PasswordIn(BaseModel):
    """重置密码。"""

    password: str = Field(min_length=6, max_length=128)


class AdminUserOut(ORMBase):
    """管理员列表项/详情。"""

    id: int
    username: str
    real_name: str | None = None
    nickname: str | None = None
    phone: str | None = None
    email: str | None = None
    dept_id: int | None = None
    role_id: int | None = None
    role_code: str | None = Field(default=None, description="主角色代码")
    data_scope: str
    is_activate: int = 1
    last_login_date: datetime | None = None
