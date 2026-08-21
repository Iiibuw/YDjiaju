"""关于我们 Pydantic 模型（对齐数据库设计文档 §4.3.5/§4.3.6）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class AboutImageIn(BaseModel):
    """图集项（嵌套于区块编辑）。"""

    url: str = Field(min_length=1, max_length=255, description="图片 URL")
    caption: str | None = Field(default=None, max_length=128, description="图片说明")
    sort: int = Field(default=0)


class AboutImageOut(ORMBase):
    id: int
    url: str
    caption: str | None = None
    sort: int = 0


class AboutSectionIn(BaseModel):
    """后台创建/更新关于区块（images 为图集，全量替换语义）。"""

    code: str = Field(min_length=1, max_length=32, description="about-yd/history/brand/contact")
    title: str = Field(min_length=1, max_length=128, description="区块标题")
    subtitle: str | None = Field(default=None, max_length=255, description="副标题")
    body: str | None = Field(default=None, description="富文本正文")
    sort: int = Field(default=0)
    is_activate: int = Field(default=1, ge=0, le=1)
    images: list[AboutImageIn] = Field(default_factory=list, description="图集（全量替换）")


class AboutSectionOut(ORMBase):
    """后台关于区块（含图集）。"""

    id: int
    code: str
    title: str
    subtitle: str | None = None
    body: str | None = None
    sort: int = 0
    is_activate: int = 1
    images: list[AboutImageOut] = Field(default_factory=list)
