"""留言 Pydantic 模型。"""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMBase


class MessageCreate(ORMBase):
    """前台留言。"""

    name: str = Field(min_length=1, max_length=64)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=128)
    content: str = Field(min_length=5, max_length=2000)


class MessageOut(ORMBase):
    """留言输出。"""

    id: int
    name: str
    phone: str | None = None
    email: str | None = None
    content: str
    status: str = "pending"
    reply_content: str | None = None
    reply_date: datetime | None = None
    created_date: datetime | None = None


class MessageReplyIn(ORMBase):
    """后台回复留言。"""

    reply_content: str = Field(min_length=1, max_length=2000)