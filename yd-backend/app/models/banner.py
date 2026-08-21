"""首页轮播图。

字段以数据库设计文档 §4.3.1 为准。
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Banner(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "banners"
    __table_args__ = (
        Index("IDX_banners_sort", "sort"),
        Index("IDX_banners_is_activate", "is_activate"),
        Index("IDX_banners_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "首页轮播图",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="标题")
    image_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片")
    link_type: Mapped[str] = mapped_column(
        Enum("product", "news", "case", "url", name="enum_banner_link_type"),
        nullable=False,
        default="product",
        server_default="product",
        comment="跳转类型",
    )
    link_target: Mapped[str] = mapped_column(String(255), nullable=False, comment="跳转目标")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="上线时间")
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="下线时间")
