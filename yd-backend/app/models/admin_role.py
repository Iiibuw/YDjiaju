"""管理员-角色多对多关联（扩展多角色，与 admin_users.role_id 主角色互补）。

字段以数据库设计文档 §4.1.5 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class AdminRole(Base, AuditMixin):
    __tablename__ = "admin_roles"
    __table_args__ = (
        UniqueConstraint("admin_id", "role_id", name="UNQ_admin_roles_admin_role"),
        Index("IDX_admin_roles_is_activate", "is_activate"),
        Index("IDX_admin_roles_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "管理员-角色关联",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="管理员 ID",
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="角色 ID",
    )
