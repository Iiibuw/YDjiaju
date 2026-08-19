"""案例 Pydantic 模型。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class CaseListItem(ORMBase):
    """GET /api/v1/public/cases 列表项。"""

    id: int
    title: str
    cover_url: str | None = None
    style: str | None = None
    area: str | None = None
    published_date: datetime = Field(description="ISO8601")
    view_count: int = 0
    category_id: int | None = None


class CaseDetail(ORMBase):
    """GET /api/v1/public/cases/{id} 详情 / 后台列表共用。"""

    id: int
    title: str
    cover_url: str
    style: str | None = None
    area: str | None = None
    description: str | None = None
    published_date: datetime
    view_count: int = 0
    category_id: int | None = None
    category: dict | None = None
    images: list[str] = Field(default_factory=list, description="案例图集 URL 列表（M2-2 用 cover 替代）")
    sort: int = 0
    is_deleted: int = 0
    created_date: datetime | None = None
    updated_date: datetime | None = None


class CaseCreate(ORMBase):
    """后台创建/更新案例。"""

    title: str = Field(min_length=2, max_length=128)
    cover_url: str = Field(min_length=8, description="封面图 URL")
    category_id: int | None = None
    style: str | None = None
    area: str | None = None
    description: str | None = None
    published_date: datetime | None = None
    sort: int = 0