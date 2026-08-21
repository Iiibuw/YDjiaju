"""客服关键词 Pydantic 模型（对齐数据库设计文档 §4.3.9）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ChatKeywordIn(BaseModel):
    """后台创建/更新客服关键词回复。"""

    keyword: str = Field(min_length=1, max_length=64, description="关键词")
    reply: str = Field(min_length=1, description="回复内容")
    enabled: int = Field(default=1, ge=0, le=1, description="是否启用")
    priority: int = Field(default=0, description="优先级（数值大者优先）")
    match_type: str = Field(default="exact", pattern="^(exact|contains|regex)$", description="匹配方式")
    is_activate: int = Field(default=1, ge=0, le=1, description="1激活 0禁用")


class ChatKeywordOut(ORMBase):
    """后台客服关键词项。"""

    id: int
    keyword: str
    reply: str
    enabled: int = 1
    priority: int = 0
    match_type: str = "exact"
    is_activate: int = 1
