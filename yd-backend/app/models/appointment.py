"""预约表（到店/咨询/定制）。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class Appointment(Base, AuditMixin):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("IDX_appointments_status_date", "status", "created_date"),
        Index("IDX_appointments_phone", "phone"),
        Index("IDX_appointments_user_id", "user_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "到店预约",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="预约会员（NULL=匿名）")
    type: Mapped[str] = mapped_column(
        Enum("visit", "consult", "custom", "other", name="enum_appointment_type"),
        nullable=False, default="visit", server_default="visit",
        comment="预约类型：visit到店/consult咨询/custom定制/other其他",
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="姓名")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="手机号")
    preferred_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="期望预约时间")
    message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="留言")
    source_page: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="来源页面 URL")
    status: Mapped[str] = mapped_column(
        Enum("pending", "following", "converted", "invalid", name="enum_appointment_status"),
        nullable=False, default="pending", server_default="pending",
        comment="跟进状态：pending待跟进/following跟进中/converted已转化/invalid无效",
    )
    assignee_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="跟进人")
    followed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最近跟进时间")
    follow_note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="跟进记录")