"""角色-权限关联。

字段以数据库设计文档 §4.1.7 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class RolePermission(Base, AuditMixin):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="UNQ_role_permissions_role_perm"),
        Index("IDX_role_permissions_is_activate", "is_activate"),
        Index("IDX_role_permissions_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "角色-权限关联",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("roles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="角色 ID",
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("permissions.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="权限 ID",
    )
