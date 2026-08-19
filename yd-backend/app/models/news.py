"""资讯主表（v1.1，含 category=company/industry 二选一简化 + is_top/is_recommend/is_published/expire_date 四状态）。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class News(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "news"
    __table_args__ = (
        # chk_news_publish_window 在 SQLite + 应用层 datetime.now() 边界场景不可靠，
        # 业务侧在 update_news() 里强制 published_date <= updated_date 即可。
        CheckConstraint(
            "expire_date IS NULL OR expire_date >= published_date",
            name="chk_news_expire_after_publish",
        ),
        Index("IDX_news_category", "category", "is_activate", "is_deleted"),
        Index("IDX_news_published", "is_published", "published_date"),
        Index("IDX_news_top", "is_top", "is_published", "published_date"),
        Index("IDX_news_recommend", "is_recommend", "is_published", "published_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "资讯主表",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="标题")
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="副标题")
    # v1.1：简化二分类
    category: Mapped[str] = mapped_column(
        Enum("company", "industry", name="enum_news_category"),
        nullable=False,
        default="company",
        server_default="company",
        comment="分类：company(企业新闻) / industry(行业资讯)",
    )
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="封面图 URL")
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="摘要")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="正文（富文本 HTML）")
    author: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="作者")
    source: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="来源（转载标注）")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="浏览量")
    published_date: Mapped["datetime | None"] = mapped_column(
        DateTime, nullable=True, comment="发布时间（NULL=草稿）"
    )
    expire_date: Mapped["datetime | None"] = mapped_column(DateTime, nullable=True, comment="截止时间（NULL=长期有效）")
    # v1.1：发布/草稿状态
    is_published: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="是否发布：1已发布 0草稿")
    # v1.1：置顶
    is_top: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="是否置顶")
    # v1.1：推荐
    is_recommend: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="是否推荐")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序值")
    is_activate: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="激活/禁用（业务状态）")