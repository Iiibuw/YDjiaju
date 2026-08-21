"""下载中心资料。

字段以数据库设计文档 §4.3.7 为准。
"""
from sqlalchemy import BigInteger, Enum, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Download(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "downloads"
    __table_args__ = (
        Index("IDX_downloads_category", "category"),
        Index("IDX_downloads_is_activate", "is_activate"),
        Index("IDX_downloads_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "下载中心",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="资料标题")
    category: Mapped[str] = mapped_column(
        Enum("catalog", "manual", "cad", "other", name="enum_download_category"),
        nullable=False,
        default="catalog",
        server_default="catalog",
        comment="资料分类",
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, comment="简介")
    file_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件 URL")
    file_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="文件大小（KB）")
    file_format: Mapped[str | None] = mapped_column(String(16), nullable=True, comment="文件格式")
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="下载次数")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
