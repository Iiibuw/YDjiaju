"""分类 Pydantic 模型（对齐数据库设计文档 §4.2.1）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class CategoryIn(BaseModel):
    """后台创建/更新分类。"""

    kind: str = Field(..., pattern="^(series|space|category)$", description="series/space/category")
    name: str = Field(min_length=1, max_length=64, description="中文名")
    name_en: str | None = Field(default=None, max_length=64, description="英文名（二期多语言）")
    icon: str | None = Field(default=None, max_length=255, description="图标 URL")
    parent_id: int | None = Field(default=None, description="父级 ID（自引用·树形）")
    sort: int = Field(default=0, description="排序")
    enabled: int = Field(default=1, ge=0, le=1, description="0禁用 1启用")


class CategoryOut(ORMBase):
    """后台分类节点（含 children 树形）。"""

    id: int
    kind: str
    name: str
    name_en: str | None = None
    icon: str | None = None
    parent_id: int | None = None
    sort: int = 0
    enabled: int = 1
    children: list["CategoryOut"] = Field(default_factory=list, description="子分类（树形）")
