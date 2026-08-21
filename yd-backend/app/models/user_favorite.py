"""会员收藏（对产品的收藏）。

字段以数据库设计文档 §4.1.10 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class UserFavorite(Base, AuditMixin):
    __tablename__ = "user_favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="UNQ_user_favorites_user_product"),
        Index("IDX_user_favorites_is_activate", "is_activate"),
        Index("IDX_user_favorites_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "会员收藏",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="会员 ID",
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="产品 ID",
    )
