"""产品 SKU 规格（颜色/材质/尺寸等组合）。

字段以数据库设计文档 §4.2.3 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class ProductSku(Base, AuditMixin):
    __tablename__ = "product_skus"
    __table_args__ = (
        UniqueConstraint("product_id", "spec_code", name="UNQ_product_skus_code"),
        Index("IDX_product_skus_product", "product_id"),
        Index("IDX_product_skus_is_activate", "is_activate"),
        Index("IDX_product_skus_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "产品规格",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属产品",
    )
    spec_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="规格名（如 胡桃色·1.8m）")
    spec_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="SKU 编码")
    price_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="价格（分）")
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="库存")
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="SKU 主图")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
