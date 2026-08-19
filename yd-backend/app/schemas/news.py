"""资讯 Pydantic 模型。"""
from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.schemas.common import ORMBase


class NewsBase:
    """资讯共享字段。"""
    title: str = Field(..., min_length=2, max_length=128, description="标题")
    subtitle: str | None = Field(None, max_length=255, description="副标题")
    category: Literal["company", "industry"] = Field("company", description="分类")
    cover_url: str | None = Field(None, max_length=255, description="封面图 URL")
    summary: str | None = Field(None, max_length=500, description="摘要")
    content: str = Field(..., min_length=1, description="正文（富文本 HTML）")
    author: str | None = Field(None, max_length=64, description="作者")
    source: str | None = Field(None, max_length=64, description="来源")
    is_top: bool = Field(False, description="是否置顶")
    is_recommend: bool = Field(False, description="是否推荐")
    sort: int = Field(0, ge=0, description="排序值")


class NewsListItem(ORMBase):
    """资讯列表项（含摘要+封面，前台列表用）。"""
    id: int
    title: str
    subtitle: str | None
    category: str
    cover_url: str | None
    summary: str | None
    author: str | None
    view_count: int
    published_date: datetime | None
    is_top: bool
    is_recommend: bool

    @field_validator("is_top", "is_recommend", mode="before")
    @classmethod
    def _int_to_bool(cls, v):
        if isinstance(v, int):
            return bool(v)
        return v


class NewsDetail(ORMBase):
    """资讯详情（含完整 content，前台/后台共用）。"""
    id: int
    title: str
    subtitle: str | None
    category: str
    cover_url: str | None
    summary: str | None
    content: str
    author: str | None
    source: str | None
    view_count: int
    published_date: datetime | None
    expire_date: datetime | None
    is_published: bool
    is_top: bool
    is_recommend: bool
    sort: int
    created_date: datetime
    updated_date: datetime

    @field_validator("is_published", "is_top", "is_recommend", mode="before")
    @classmethod
    def _int_to_bool(cls, v):
        if isinstance(v, int):
            return bool(v)
        return v


class NewsCreate(ORMBase):
    """后台创建/更新资讯。"""
    title: str = Field(..., min_length=2, max_length=128)
    subtitle: str | None = Field(None, max_length=255)
    category: Literal["company", "industry"] = "company"
    cover_url: str | None = Field(None, max_length=255)
    summary: str | None = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    author: str | None = None
    source: str | None = None
    is_published: bool = False
    is_top: bool = False
    is_recommend: bool = False
    sort: int = 0
    published_date: datetime | None = None
    expire_date: datetime | None = None


class NewsListOut(ORMBase):
    """分页列表响应容器。"""
    items: list[NewsListItem]
    total: int
    page: int
    page_size: int