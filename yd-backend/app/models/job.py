"""招聘岗位表（v1.1，含 category=social/campus + 5 阶段）。"""
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


class Job(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint(
            "salary_min_cents IS NULL OR salary_max_cents IS NULL OR salary_min_cents <= salary_max_cents",
            name="chk_jobs_salary",
        ),
        CheckConstraint(
            "expire_date IS NULL OR expire_date >= publish_date",
            name="chk_jobs_date_range",
        ),
        Index("IDX_jobs_category", "category", "is_activate", "is_deleted"),
        Index("IDX_jobs_publish", "publish_date", "expire_date"),
        Index("IDX_jobs_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "招聘岗位",
        },
    )

    id: Mapped[int] = mapped_column(Integer().with_variant(BigInteger, "mysql"), primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False, comment="岗位名称")
    category: Mapped[str] = mapped_column(
        Enum("social", "campus", name="enum_jobs_category"),
        nullable=False,
        default="social",
        server_default="social",
        comment="分类：social(社招) / campus(校招)",
    )
    department: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="部门")
    location: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="工作地点")
    salary_min_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="最低薪资（分）")
    salary_max_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="最高薪资（分）")
    headcount: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1", comment="招聘人数")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="岗位职责")
    requirement: Mapped[str | None] = mapped_column(Text, nullable=True, comment="任职要求")
    publish_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), server_default=func.now(), comment="发布时间"
    )
    expire_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="截止时间")
    is_activate: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="激活/禁用")