"""购物车明细。

字段以数据库设计文档 §4.5.3 为准；数量范围 CHECK 约束。
"""
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class CartItem(Base, AuditMixin):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "sku_id", name="UNQ_cart_items_user_sku"),
        CheckConstraint("quantity > 0 AND quantity <= 999", name="chk_cart_items_quantity"),
        Index("IDX_cart_items_is_activate", "is_activate"),
        Index("IDX_cart_items_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "购物车",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="会员",
    )
    sku_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("product_skus.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="SKU",
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1", comment="数量")
    selected: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default="1", comment="结算选中"
    )
