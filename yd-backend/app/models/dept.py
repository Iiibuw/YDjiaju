"""部门表（树形）。"""
from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Dept(Base, AuditMixin):
    """部门（自引用树）。新增于 v1.1。"""

    __tablename__ = "depts"
    __table_args__ = (
        UniqueConstraint("code", name="UNQ_depts_code"),
        CheckConstraint("parent_id IS NULL OR parent_id <> id", name="chk_depts_no_self_parent"),
        Index("IDX_depts_parent_id", "parent_id"),
        Index("IDX_depts_is_activate", "is_activate"),
        Index("IDX_depts_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "部门表（树形）",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="部门名称")
    code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="部门编码")
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("depts.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        comment="上级部门（自引用）",
    )
    sort: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="同级排序")
    leader_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="部门负责人",
    )
    path: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="层级路径 ,1,3,7,")
