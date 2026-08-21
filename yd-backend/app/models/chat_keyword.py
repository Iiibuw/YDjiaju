"""客服关键词回复。

字段以数据库设计文档 §4.3.9 为准；含软删除。
"""
from sqlalchemy import Enum, Index, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class ChatKeyword(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "chat_keywords"
    __table_args__ = (
        Index("IDX_chat_keywords_enabled_priority", "enabled", "priority", "is_activate"),
        Index("IDX_chat_keywords_keyword", "keyword"),
        Index("IDX_chat_keywords_is_activate", "is_activate"),
        Index("IDX_chat_keywords_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "客服关键词回复",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(64), nullable=False, comment="关键词")
    reply: Mapped[str] = mapped_column(Text, nullable=False, comment="回复内容")
    enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="是否启用")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="优先级")
    match_type: Mapped[str] = mapped_column(
        Enum("exact", "contains", "regex", name="enum_chat_match_type"),
        nullable=False,
        default="exact",
        server_default="exact",
        comment="匹配方式",
    )
