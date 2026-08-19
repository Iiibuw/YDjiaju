"""访客留言表（联系我们表单 / 留言板）。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Message(Base, AuditMixin, SoftDeleteMixin):
    """前台留言。新增于 M2-2-B。"""

    __tablename__ = "messages"
    __table_args__ = (
        Index("IDX_messages_status", "status", "is_deleted"),
        Index("IDX_messages_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "访客留言",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="称呼")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="联系电话")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="邮箱")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="留言内容")
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="pending", server_default="pending",
        comment="pending/replied/archived",
    )
    reply_content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="后台回复内容")
    reply_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="回复时间")