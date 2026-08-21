"""站点配置 Pydantic 模型（对齐数据库设计文档 §4.3.8）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class SiteConfigIn(BaseModel):
    """后台创建/更新站点配置。"""

    config_key: str = Field(min_length=1, max_length=64, description="配置键（唯一）")
    config_value: str = Field(min_length=1, description="配置值")
    value_type: str = Field(default="string", pattern="^(string|number|json|bool)$", description="值类型")
    category: str | None = Field(default=None, max_length=32, description="配置分类")
    description: str | None = Field(default=None, max_length=255, description="说明")
    is_activate: int = Field(default=1, ge=0, le=1, description="1激活 0禁用")


class SiteConfigOut(ORMBase):
    """后台站点配置项。"""

    id: int
    config_key: str
    config_value: str
    value_type: str = "string"
    category: str | None = None
    description: str | None = None
    is_activate: int = 1
