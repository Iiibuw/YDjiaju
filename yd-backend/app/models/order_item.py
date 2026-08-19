"""订单明细表。"""
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class OrderItem(Base, AuditMixin):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "subtotal_cents = price_cents * quantity AND quantity > 0 AND price_cents >= 0",
            name="chk_order_items_amount",
        ),
        Index("IDX_order_items_order_id", "order_id"),
        Index("IDX_order_items_product_id", "product_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "订单明细",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属订单")
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="产品 ID")
    product_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="产品名（快照）")
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="产品封面（快照）")
    price_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="单价（快照·分）")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, comment="数量")
    subtotal_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="小计（分）")