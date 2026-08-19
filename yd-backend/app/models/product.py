"""产品主表（v1.1，含 status 三态枚举 + product_code + is_top）。"""
from sqlalchemy import BigInteger, CheckConstraint, Enum, ForeignKey, Index, Integer, JSON, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Product(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "products"
    __table_args__ = (
        # 审核新增：v1.1 三选一至少其一
        CheckConstraint(
            "category_id IS NOT NULL OR space_id IS NOT NULL OR series_id IS NOT NULL",
            name="chk_products_category_or_space",
        ),
        # 审核新增：草稿不允许置顶
        CheckConstraint(
            "NOT (status = 'draft' AND is_top = 1)",
            name="chk_products_draft_no_top",
        ),
        CheckConstraint(
            "min_price_cents IS NULL OR max_price_cents IS NULL OR min_price_cents <= max_price_cents",
            name="chk_products_amount",
        ),
        UniqueConstraint("product_code", name="UNQ_products_product_code"),
        Index("IDX_products_category", "category_id", "status", "is_deleted"),
        Index("IDX_products_series", "series_id", "status", "is_deleted"),
        Index("IDX_products_space", "space_id", "status", "is_deleted"),
        Index("IDX_products_support_order", "support_order", "status"),
        Index("IDX_products_status_top", "status", "is_top", "sort"),  # v1.1 新增
        Index("IDX_products_created_date", "created_date"),
        # 注意：FULLTEXT 索引在 MySQL 8.0 上可选添加（ORM 暂不直接支持，已通过 install_all.sql 创建）
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "产品主表",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    product_code: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="v1.1 产品编号（唯一）")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="产品名")
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="副标题")
    series_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="所属系列（如胡桃禮）",
    )
    space_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="所属空间分类 id",
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="品类（PRD 二选一，v1.1 后允许为空）",
    )
    min_price_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="最低价（分）")
    max_price_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="最高价（分）")
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="封面图片 URL")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="产品描述（富文本）")
    specs_summary: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="规格参数摘要")
    extra_specs: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="规格参数（JSON 串）")
    other_images_json: Mapped[list | None] = mapped_column("other_images", JSON, nullable=True, comment="其它图片 URL（JSON 串，v1.1 新增）")
    support_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="是否支持在线下单")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序值")
    # v1.1：status 三态枚举（draft / on_sale / off_sale）
    status: Mapped[str] = mapped_column(
        Enum("draft", "on_sale", "off_sale", name="enum_product_status"),
        nullable=False,
        default="draft",
        server_default="draft",
        comment="发布状态：draft(草稿) / on_sale(上架) / off_sale(下架)",
    )
    # v1.1：是否置顶
    is_top: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="是否置顶（0/1）")
