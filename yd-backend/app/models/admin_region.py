"""管理员-区域管辖（与 admin_users.data_scope 配合做数据隔离）。

字段以数据库设计文档 §4.1.8 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class AdminRegion(Base, AuditMixin):
    __tablename__ = "admin_regions"
    __table_args__ = (
        UniqueConstraint("admin_id", "region_code", name="UNQ_admin_regions_admin_region"),
        Index("IDX_admin_regions_is_activate", "is_activate"),
        Index("IDX_admin_regions_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "管理员-区域管辖",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="管理员 ID",
    )
    region_code: Mapped[str] = mapped_column(String(32), nullable=False, comment="区域代码")
