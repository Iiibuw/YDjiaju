"""后台操作审计日志（合规要求）。

字段以数据库设计文档 §4.1.13 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, JSON, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class AuditLog(Base, AuditMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("IDX_audit_logs_admin_id", "admin_id"),
        Index("IDX_audit_logs_resource", "resource", "resource_id"),
        Index("IDX_audit_logs_action", "action"),
        Index("IDX_audit_logs_created_date", "created_date"),
        Index("IDX_audit_logs_is_activate", "is_activate"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "操作审计",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    admin_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="操作人",
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作类型（如 product.create）")
    resource: Mapped[str] = mapped_column(String(32), nullable=False, comment="资源类型")
    resource_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="资源 ID")
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True, comment="变更详情（脱敏）")
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="操作 IP")
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="浏览器 UA")
