"""产品图片。

字段以数据库设计文档 §4.2.4 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class ProductImage(Base, AuditMixin):
    __tablename__ = "product_images"
    __table_args__ = (
        Index("IDX_product_images_product", "product_id"),
        Index("IDX_product_images_is_activate", "is_activate"),
        Index("IDX_product_images_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "产品图片",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属产品",
    )
    url: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片 URL")
    alt: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="替代文本")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
