"""案例图集。

字段以数据库设计文档 §4.3.3 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class CaseImage(Base, AuditMixin):
    __tablename__ = "case_images"
    __table_args__ = (
        Index("IDX_case_images_case", "case_id"),
        Index("IDX_case_images_is_activate", "is_activate"),
        Index("IDX_case_images_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "案例图集",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cases.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="所属案例",
    )
    url: Mapped[str] = mapped_column(String(255), nullable=False, comment="图片 URL")
    caption: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="图片说明")
    sort: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="排序")
