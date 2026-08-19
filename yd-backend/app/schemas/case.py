"""案例 Pydantic 模型。"""
from pydantic import Field

from app.schemas.common import ORMBase


class CaseListItem(ORMBase):
    """GET /api/v1/public/cases 列表项。"""

    id: int
    title: str
    cover_url: str | None = None
    style: str | None = None
    area: str | None = None
    published_date: str = Field(description="ISO8601")
    view_count: int = 0
    category_id: int | None = None


class CaseDetail(ORMBase):
    """GET /api/v1/public/cases/{id} 详情。"""

    id: int
    title: str
    cover_url: str
    style: str | None = None
    area: str | None = None
    description: str | None = None
    published_date: str
    view_count: int = 0
    category: dict | None = None
    images: list[str] = Field(default_factory=list, description="case_images 表的 URL 列表")
