"""留言服务层：前台提交 + 后台查询/回复。"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut, MessageReplyIn


def create_message(payload: MessageCreate, db: Session) -> MessageOut:
    m = Message(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        content=payload.content,
        status="pending",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return MessageOut.model_validate(m)


def list_messages_admin(
    db: Session,
    *,
    status_filter: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[MessageOut], int]:
    q = select(Message).where(Message.is_deleted == 0)
    if status_filter:
        q = q.where(Message.status == status_filter)
    if keyword:
        like = f"%{keyword}%"
        q = q.where((Message.name.like(like)) | (Message.content.like(like)))
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Message.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    return [MessageOut.model_validate(r) for r in rows], total


def reply_message(db: Session, message_id: int, payload: MessageReplyIn) -> MessageOut | None:
    m = db.get(Message, message_id)
    if not m or m.is_deleted:
        return None
    m.reply_content = payload.reply_content
    m.reply_date = datetime.utcnow()
    m.status = "replied"
    db.commit()
    db.refresh(m)
    return MessageOut.model_validate(m)


def delete_message(db: Session, message_id: int) -> bool:
    m = db.get(Message, message_id)
    if not m or m.is_deleted:
        return False
    m.is_deleted = 1
    m.deleted_at = datetime.utcnow()
    db.commit()
    return True


__all__ = ["create_message", "list_messages_admin", "reply_message", "delete_message"]