"""会员收货地址簿。

字段以数据库设计文档 §4.1.9 为准。
"""
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class UserAddress(Base, AuditMixin):
    __tablename__ = "user_addresses"
    __table_args__ = (
        Index("IDX_user_addresses_user_id", "user_id"),
        Index("IDX_user_addresses_region_code", "region_code"),
        Index("IDX_user_addresses_is_activate", "is_activate"),
        Index("IDX_user_addresses_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "会员收货地址",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="所属会员",
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="收货人姓名")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="收货人手机号")
    region_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="省市区代码")
    region_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="省市区文本")
    address: Mapped[str] = mapped_column(String(255), nullable=False, comment="详细地址")
    store_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="归属门店（数据隔离）")
    is_default: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0", comment="是否默认地址"
    )
