"""关于我们图集（每个区块的支持图集）。

字段以数据库设计文档 §4.3.6 为准；含软删除。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class AboutImage(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "about_images"
    __table_args__ = (
        Index("IDX_about_images_section", "section_id"),
        Index("IDX_about_images_is_activate", "is_activate"),
        Index("IDX_about_images_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "关于我们图集",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("about_sections.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属区块",
    )
    url: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片 URL")
    caption: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="图片说明")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
