"""关于我们区块（about-yd / history / brand / contact）。

字段以数据库设计文档 §4.3.5 为准；含软删除。
"""
from sqlalchemy import Integer, SmallInteger, String, Text, UniqueConstraint, Index

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class AboutSection(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "about_sections"
    __table_args__ = (
        UniqueConstraint("code", name="UNQ_about_sections_code"),
        Index("IDX_about_sections_is_activate", "is_activate"),
        Index("IDX_about_sections_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "关于我们区块",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False, comment="区块代码（about-yd/history/brand/contact）")
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="区块标题")
    subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="副标题")
    body: Mapped[str | None] = mapped_column(Text, nullable=True, comment="富文本正文")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
