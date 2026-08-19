"""后台管理员表。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Enum,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import hash_password  # noqa: F401  # 仅用于 IDE
from app.db.base import Base
from app.models.mixins import AuditMixin


class AdminUser(Base, AuditMixin):
    """后台管理员。

    数据隔离：data_scope 决定可见数据范围（ALL / REGION / STORE / SELF）。
    """

    __tablename__ = "admin_users"
    __table_args__ = (
        UniqueConstraint("username", name="UNQ_admin_users_username"),
        CheckConstraint("failed_attempts <= 10", name="chk_admin_users_failed_attempts"),
        Index("IDX_admin_users_phone", "phone"),
        Index("IDX_admin_users_dept_id", "dept_id"),
        Index("IDX_admin_users_role_id", "role_id"),
        Index("IDX_admin_users_is_activate", "is_activate"),
        Index("IDX_admin_users_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "后台管理员",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, comment="登录名（唯一）")
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment="bcrypt 哈希")
    real_name: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="姓名")
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="昵称")
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True, comment="手机号")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="邮箱")
    gender: Mapped[int | None] = mapped_column(SmallInteger, nullable=True, comment="0未知 1男 2女")
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="头像")
    post: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="岗位")
    dept_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="部门编号（FK → depts.id）",
    )
    role_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="角色编号（FK → roles.id，主角色）",
    )
    failed_attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="登录失败次数")
    locked_until: Mapped[datetime | None] = mapped_column(nullable=True, comment="锁定截止时间")
    last_login_date: Mapped[datetime | None] = mapped_column(nullable=True, comment="最近登录时间")
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="最近登录 IP（IPv4/IPv6）")
    data_scope: Mapped[str] = mapped_column(
        Enum("ALL", "REGION", "STORE", "SELF", name="enum_admin_data_scope"),
        nullable=False,
        default="REGION",
        server_default="REGION",
        comment="数据范围：ALL/REGION/STORE/SELF",
    )

    # 业务关联（延迟求值，避免循环导入）
    def get_region_codes(self) -> list[str]:
        # TODO M2: 通过 admin_regions 查
        return []



