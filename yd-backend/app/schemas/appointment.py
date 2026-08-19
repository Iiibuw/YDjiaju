"""预约 Pydantic 模型。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class AppointmentCreate(ORMBase):
    """预约请求（前台/游客）。"""

    type: str = Field(default="visit", description="visit/consult/custom/other")
    name: str = Field(min_length=1, max_length=64)
    phone: str = Field(pattern=r"^1[3-9]\d{9}$")
    preferred_date: datetime | None = None
    message: str | None = Field(default=None, max_length=2000)
    source_page: str | None = Field(default=None, max_length=128)


class AppointmentOut(ORMBase):
    """预约输出。"""

    id: int
    type: str
    name: str
    phone: str
    preferred_date: datetime | None = None
    message: str | None = None
    source_page: str | None = None
    status: str = "pending"
    follow_note: str | None = None
    created_date: datetime | None = None


class AppointmentStatusUpdate(ORMBase):
    """后台更新预约跟进状态。"""

    status: str = Field(description="pending/following/converted/invalid")
    follow_note: str | None = None