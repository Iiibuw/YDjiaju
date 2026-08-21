"""权限点（RBAC 最小权限单元，按钮级 / API 级）。

字段以数据库设计文档 §4.1.6 为准。
"""
from sqlalchemy import BigInteger, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Permission(Base, AuditMixin):
    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("code", name="UNQ_permissions_code"),
        Index("IDX_permissions_module", "module"),
        Index("IDX_permissions_is_activate", "is_activate"),
        Index("IDX_permissions_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "权限点",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, comment="权限代码（如 product.create）")
    module: Mapped[str] = mapped_column(String(32), nullable=False, comment="所属模块")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="权限描述")
