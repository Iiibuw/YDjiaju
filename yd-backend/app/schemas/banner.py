"""轮播图 Pydantic 模型（对齐数据库设计文档 §4.3.1）。"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class BannerIn(BaseModel):
    """后台创建/更新轮播图。"""

    title: str = Field(min_length=1, max_length=128, description="标题")
    image_url: str = Field(min_length=1, max_length=255, description="图片 URL")
    link_type: str = Field(default="product", pattern="^(product|news|case|url)$", description="跳转类型")
    link_target: str = Field(default="", max_length=255, description="跳转目标")
    sort: int = Field(default=0, description="排序")
    start_date: datetime | None = Field(default=None, description="上线时间")
    end_date: datetime | None = Field(default=None, description="下线时间")
    is_activate: int = Field(default=1, ge=0, le=1, description="1激活 0禁用")


class BannerOut(ORMBase):
    """后台轮播图列表项/详情。"""

    id: int
    title: str
    image_url: str
    link_type: str
    link_target: str
    sort: int = 0
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_activate: int = 1
