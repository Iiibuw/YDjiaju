"""招聘 Pydantic 模型。"""
from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import ORMBase


class JobListItem(ORMBase):
    """岗位列表项（前台/后台列表用）。"""
    id: int
    title: str
    category: str
    department: str | None
    location: str | None
    salary_min_cents: int | None
    salary_max_cents: int | None
    headcount: int
    publish_date: datetime
    expire_date: datetime | None


class JobDetail(ORMBase):
    """岗位详情（含 description/requirement 富文本）。"""
    id: int
    title: str
    category: str
    department: str | None
    location: str | None
    salary_min_cents: int | None
    salary_max_cents: int | None
    headcount: int
    description: str | None
    requirement: str | None
    publish_date: datetime
    expire_date: datetime | None
    created_date: datetime
    updated_date: datetime


class JobCreate(ORMBase):
    """后台创建/更新岗位。"""
    title: str = Field(..., min_length=2, max_length=128)
    category: Literal["social", "campus"] = "social"
    department: str | None = None
    location: str | None = None
    salary_min_cents: int | None = Field(None, ge=0)
    salary_max_cents: int | None = Field(None, ge=0)
    headcount: int = 1
    description: str | None = None
    requirement: str | None = None
    publish_date: datetime | None = None
    expire_date: datetime | None = None
    is_activate: bool = True

    @model_validator(mode="after")
    def _check_salary(self):
        if self.salary_min_cents is not None and self.salary_max_cents is not None:
            if self.salary_min_cents > self.salary_max_cents:
                raise ValueError("salary_min_cents 不能大于 salary_max_cents")
        return self


class JobApplicationCreate(ORMBase):
    """前台投递岗位（公开 API，无须登录）。"""
    job_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=64)
    phone: str = Field(..., min_length=5, max_length=20, description="手机号")
    email: str | None = Field(None, max_length=128)
    region_code: str | None = None
    resume_url: str | None = Field(None, max_length=255)


class JobApplicationOut(ORMBase):
    """投递记录详情（后台管理用）。"""
    id: int
    job_id: int
    job_title: str | None = None  # 后端 join 填充
    name: str
    phone: str
    email: str | None
    region_code: str | None
    resume_url: str | None
    stage: str
    reject_reason: str | None
    applied_date: datetime
    screening_date: datetime | None
    interview_date: datetime | None
    offer_date: datetime | None
    closed_date: datetime | None
    admin_note: str | None
    created_date: datetime


class JobApplicationListOut(ORMBase):
    items: list[JobApplicationOut]
    total: int
    page: int
    page_size: int


class JobListOut(ORMBase):
    items: list[JobListItem]
    total: int
    page: int
    page_size: int