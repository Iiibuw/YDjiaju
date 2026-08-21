"""订单主表。"""
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, ForeignKey, Index, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Order(Base, AuditMixin):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("order_no", name="UNQ_orders_order_no"),
        CheckConstraint(
            "total_cents >= 0 AND shipping_cents >= 0 AND discount_cents >= 0 "
            "AND final_cents = total_cents + shipping_cents - discount_cents",
            name="chk_orders_amount",
        ),
        Index("IDX_orders_user_status", "user_id", "status", "created_date"),
        Index("IDX_orders_status_date", "status", "created_date"),
        Index("IDX_orders_region_store", "region_code", "store_code"),
        Index("IDX_orders_final_cents", "final_cents"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "订单主表",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), nullable=False, comment="订单号（唯一）")
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="下单人（NULL=游客）")
    receiver_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="收货人姓名（快照）")
    receiver_phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="收货人手机（快照）")
    receiver_address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="收货地址文本（快照）")
    status: Mapped[str] = mapped_column(
        Enum("pending", "paid", "shipped", "completed", "refunding", "refunded", "closed", name="enum_order_status"),
        nullable=False, default="pending", server_default="pending",
        comment="订单状态：pending待付款/paid已付款/shipped已发货/completed已完成/closed已关闭",
    )
    total_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="商品总额（分）")
    shipping_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="运费（分）")
    discount_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="优惠（分）")
    final_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="实付金额（分）")
    remark: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="用户备注")
    paid_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="支付时间")
    shipped_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="发货时间")
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="完成时间")
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="关闭时间")
    address_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user_addresses.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="收货地址快照",
    )
    region_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="收货区域")
    store_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="归属门店")