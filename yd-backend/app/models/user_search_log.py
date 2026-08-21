"""前台会员搜索关键词记录（推荐 / 分析用）。

字段以数据库设计文档 §4.1.11 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class UserSearchLog(Base, AuditMixin):
    __tablename__ = "user_search_logs"
    __table_args__ = (
        Index("IDX_user_search_logs_user_id", "user_id"),
        Index("IDX_user_search_logs_keyword", "keyword"),
        Index("IDX_user_search_logs_is_activate", "is_activate"),
        Index("IDX_user_search_logs_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "会员搜索记录",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="搜索用户（NULL = 匿名）",
    )
    keyword: Mapped[str] = mapped_column(String(128), nullable=False, comment="搜索关键词")
    result_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="结果数")
