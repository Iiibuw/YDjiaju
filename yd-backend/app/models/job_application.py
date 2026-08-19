"""岗位投递记录表（5 阶段：applied/screening/interview/offer/rejected）。"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class JobApplication(Base, AuditMixin):
    __tablename__ = "job_applications"
    __table_args__ = (
        # 审核新增：防匿名重复投递
        UniqueConstraint("job_id", "phone", name="UNQ_job_applications_job_phone"),
        Index("IDX_job_applications_job_id", "job_id"),
        Index("IDX_job_applications_user_id", "user_id"),
        Index("IDX_job_applications_stage", "stage"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "岗位投递记录",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="投递岗位 id")
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="投递人（NULL=匿名）")
    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="姓名")
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment="手机号")
    email: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="邮箱")
    resume_url: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="简历 URL")
    region_code: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="投递区域")
    stage: Mapped[str] = mapped_column(
        Enum("applied", "screening", "interview", "offer", "rejected", name="enum_application_stage"),
        nullable=False,
        default="applied",
        server_default="applied",
        comment="5 阶段状态",
    )
    reject_reason: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="拒绝原因")
    applied_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now(), comment="投递时间"
    )
    screening_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="初筛时间")
    interview_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="面试时间")
    offer_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="Offer 时间")
    closed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="终结时间")
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True, comment="内部备注")
    is_activate: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="激活/禁用")