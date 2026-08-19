"""部门（树形）Pydantic 模型。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class DeptNode(ORMBase):
    """树节点（自引用）。"""

    id: int
    name: str
    code: str | None = None
    parent_id: int | None = None
    sort: int = 0
    leader_id: int | None = None
    path: str | None = None
    is_activate: int = 1
    created_date: datetime | None = None
    updated_date: datetime | None = None


class DeptCreate(ORMBase):
    """后台创建/更新部门。"""

    name: str = Field(min_length=1, max_length=64)
    code: str | None = None
    parent_id: int | None = None
    sort: int = 0
    leader_id: int | None = None
    is_activate: bool = True