"""产品 Pydantic 模型（与技术文档 §4.3.2/4.3.3 对齐）。"""
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ProductListItem(ORMBase):
    """GET /api/v1/public/products 列表项（v1.1 含 product_code/is_top）。"""

    id: int
    product_code: str | None = Field(default=None, description="v1.1 产品编号")
    name: str
    subtitle: str | None = None
    cover_url: str | None = None
    min_price_cents: int | None = None
    max_price_cents: int | None = None
    price_yuan: str | None = Field(default=None, description="展示用价格字符串")
    is_top: int = Field(description="v1.1 是否置顶")
    status: str = Field(description="draft / on_sale / off_sale")
    category_id: int | None = None
    series_id: int | None = None
    space_id: int | None = None


class ProductDetail(ORMBase):
    """GET /api/v1/public/products/{id} 详情（v1.1）。"""

    id: int
    product_code: str | None = None
    name: str
    subtitle: str | None = None
    cover_url: str | None = None
    other_images: list[str] = Field(default_factory=list, description="v1.1 其它图片（JSON 解析）")
    description: str | None = None
    specs: dict | None = Field(default=None, description="v1.1 extra_specs 解析")
    min_price_cents: int | None = None
    max_price_cents: int | None = None
    is_top: int = 0
    status: str
    series: dict | None = None
    space: dict | None = None
    category: dict | None = None


class ProductCreate(BaseModel):
    """后台 POST /api/v1/admin/products 请求体。"""

    product_code: str | None = Field(default=None, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    subtitle: str | None = Field(default=None, max_length=255)
    series_id: int | None = None
    space_id: int | None = None
    category_id: int | None = None
    min_price_cents: int | None = Field(default=None, ge=0)
    max_price_cents: int | None = Field(default=None, ge=0)
    cover_url: str | None = None
    other_images: list[str] = Field(default_factory=list)
    description: str | None = None
    specs: dict | None = None
    support_order: int = Field(default=0, ge=0, le=1)
    sort: int = Field(default=0)
    status: str = Field(default="draft", pattern="^(draft|on_sale|off_sale)$")
    is_top: int = Field(default=0, ge=0, le=1)

class ProductUpdate(BaseModel):
    """后台 PUT /api/v1/admin/products/{id} 请求体（部分字段更新，exclude_unset）。"""

    product_code: str | None = Field(default=None, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    subtitle: str | None = Field(default=None, max_length=255)
    series_id: int | None = None
    space_id: int | None = None
    category_id: int | None = None
    min_price_cents: int | None = Field(default=None, ge=0)
    max_price_cents: int | None = Field(default=None, ge=0)
    cover_url: str | None = None
    other_images: list[str] | None = None
    description: str | None = None
    specs: dict | None = None
    support_order: int | None = Field(default=None, ge=0, le=1)
    sort: int | None = Field(default=None)
    status: str | None = Field(default=None, pattern="^(draft|on_sale|off_sale)$")
    is_top: int | None = Field(default=None, ge=0, le=1)

