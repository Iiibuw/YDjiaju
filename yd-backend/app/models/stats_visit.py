"""前台页面访问日志（PV/UV 统计基础）。

字段以数据库设计文档 §4.1.12 为准。
"""
from sqlalchemy import BigInteger, Enum, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class StatsVisit(Base, AuditMixin):
    __tablename__ = "stats_visit"
    __table_args__ = (
        Index("IDX_stats_visit_user_id", "user_id"),
        Index("IDX_stats_visit_path", "path"),
        Index("IDX_stats_visit_created_date", "created_date"),
        Index("IDX_stats_visit_is_activate", "is_activate"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "访问日志",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="访问用户（NULL=游客）",
    )
    path: Mapped[str] = mapped_column(String(255), nullable=False, comment="访问路径")
    referer: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="来源页面")
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="访问 IP")
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="浏览器 UA")
    device_type: Mapped[str | None] = mapped_column(
        Enum("desktop", "mobile", "tablet", name="enum_device_type"),
        nullable=True,
        comment="设备类型",
    )
