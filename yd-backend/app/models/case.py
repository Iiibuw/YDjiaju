"""案例表。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Case(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "cases"
    __table_args__ = (
        Index("IDX_cases_category", "category_id", "is_activate", "is_deleted"),
        Index("IDX_cases_published", "published_date"),
        Index("IDX_cases_is_activate", "is_activate"),
        Index("IDX_cases_is_deleted", "is_deleted"),
        Index("IDX_cases_created_date", "created_date"),
        # 全文索引由 install_all.sql 创建
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "案例展示",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="案例标题")
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="案例分类（categories.type=space 等）",
    )
    cover_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="封面图")
    style: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="风格")
    area: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="面积")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="案例详情（富文本）")
    published_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="发布时间")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="浏览量")
