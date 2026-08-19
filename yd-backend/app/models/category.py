"""分类字典表（系列 / 空间 / 品类 三类）。

注意：`type` 是 SQLAlchemy Declarative 保留字段，改用 Python 属性 `kind` 对应 `type` 列。
"""
from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Category(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("parent_id IS NULL OR parent_id <> id", name="chk_categories_no_self_parent"),
        Index("IDX_categories_type_status", "type", "is_activate"),
        Index("IDX_categories_parent_id", "parent_id"),
        Index("IDX_categories_is_deleted", "is_deleted"),
        Index("IDX_categories_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "产品分类字典",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 列名 'type' 映射到 Python 属性 kind（SQLAlchemy 保留字规避）
    kind: Mapped[str] = mapped_column(
        "type",
        Enum("series", "space", "category", name="enum_category_type"),
        nullable=False,
        comment="分类类型：series(系列) / space(空间) / category(品类)",
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="中文名")
    name_en: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="英文名")
    icon: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="图标 URL")
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="父级 ID（自引用）",
    )
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
    # 'status' 在 SQLAlchemy 2.0 中虽是合法标识符，但保留字段语义不清晰；显式映射
    enabled: Mapped[int] = mapped_column(
        "status",
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
        comment="0禁用 1启用",
    )
