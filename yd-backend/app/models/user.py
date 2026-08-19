"""前台会员表。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("phone", name="UNQ_users_phone"),
        Index("IDX_users_is_activate", "is_activate"),
        Index("IDX_users_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "前台会员",
        },
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(BigInteger(), "mysql"), primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="手机号（登录账号）")
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="bcrypt 哈希")
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="昵称")
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="头像 URL")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="邮箱")
    gender: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment="0未知 1男 2女")
    failed_attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="登录失败次数（防爆破）")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="锁定截止时间")
    last_login_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最近登录时间")
