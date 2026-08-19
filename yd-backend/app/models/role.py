"""角色表（RBAC）。"""
from sqlalchemy import BigInteger, Enum, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("code", name="UNQ_roles_code"),
        Index("IDX_roles_is_activate", "is_activate"),
        Index("IDX_roles_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "角色表",
        },
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(BigInteger(), "mysql"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="角色名称")
    code: Mapped[str] = mapped_column(String(32), nullable=False, comment="角色代码（唯一，如 admin/editor/product）")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="角色描述")
    data_scope: Mapped[str] = mapped_column(
        Enum("ALL", "REGION", "STORE", "SELF", name="enum_role_data_scope"),
        nullable=False,
        default="REGION",
        server_default="REGION",
        comment="数据范围",
    )
    sort: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="排序")
