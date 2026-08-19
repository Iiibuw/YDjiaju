"""Pydantic 通用模型：API 响应 + 分页。"""
from datetime import datetime
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

T = TypeVar("T")

# 自动把 datetime → ISO 字符串（避免前端再次 toLocaleDateString）
DateTimeStr = Annotated[datetime, PlainSerializer(lambda v: v.isoformat() if v else "", return_type=str)]


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式（与技术文档 §4 通用约定对齐）。"""

    code: int = Field(default=0, description="0=成功；非0=失败")
    message: str = Field(default="ok", description="提示信息")
    data: T | None = Field(default=None, description="业务数据")
    trace_id: str | None = Field(default=None, description="请求追踪 ID")


class PaginationMeta(BaseModel):
    """分页元数据。"""

    total: int = Field(ge=0, description="总记录数")
    page: int = Field(ge=1, description="当前页")
    page_size: int = Field(ge=1, le=100, description="页大小")
    total_pages: int = Field(ge=0, description="总页数")


class PageData(BaseModel, Generic[T]):
    """分页数据容器。"""

    items: list[T] = Field(default_factory=list)
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int = Field(ge=0)


class ORMBase(BaseModel):
    """ORM 序列化基类：允许从 SQLAlchemy 模型读字段 + 自动转 datetime → ISO。"""

    model_config = ConfigDict(from_attributes=True)