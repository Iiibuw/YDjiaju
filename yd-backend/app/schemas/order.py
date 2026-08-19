"""订单 Pydantic 模型。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class OrderItemCreate(ORMBase):
    """下单明细。"""

    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class OrderCreate(ORMBase):
    """下单请求。"""

    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)
    receiver_name: str = Field(min_length=1, max_length=64)
    receiver_phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    receiver_address: str = Field(min_length=5, max_length=255)
    remark: str | None = Field(default=None, max_length=500)


class OrderItemOut(ORMBase):
    """订单明细输出。"""

    id: int
    product_id: int
    product_name: str
    cover_url: str | None = None
    price_cents: int
    quantity: int
    subtotal_cents: int


class OrderOut(ORMBase):
    """订单输出。"""

    id: int
    order_no: str
    status: str
    total_cents: int
    shipping_cents: int
    discount_cents: int
    final_cents: int
    receiver_name: str | None = None
    receiver_phone: str | None = None
    receiver_address: str | None = None
    remark: str | None = None
    created_date: datetime | None = None
    paid_date: datetime | None = None
    shipped_date: datetime | None = None
    completed_date: datetime | None = None
    closed_date: datetime | None = None
    items: list[OrderItemOut] = Field(default_factory=list)


class OrderStatusUpdate(ORMBase):
    """后台更新订单状态。"""

    status: str = Field(description="paid/shipped/completed/closed")