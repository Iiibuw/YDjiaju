"""客服关键词服务层（后台）。"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chat_keyword import ChatKeyword
from app.schemas.chat_keyword import ChatKeywordIn, ChatKeywordOut


def list_chat_keywords(
    db: Session,
    *,
    keyword: str | None = None,
    enabled: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ChatKeywordOut], int]:
    q = select(ChatKeyword).where(ChatKeyword.is_deleted == 0)
    if enabled is not None:
        q = q.where(ChatKeyword.enabled == enabled)
    if keyword:
        q = q.where(ChatKeyword.keyword.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(ChatKeyword.priority.desc(), ChatKeyword.id)
    q = q.offset((page - 1) * page_size).limit(page_size)
    items = [ChatKeywordOut.model_validate(r) for r in db.execute(q).scalars().all()]
    return items, total


def get_chat_keyword(db: Session, keyword_id: int) -> ChatKeyword | None:
    c = db.get(ChatKeyword, keyword_id)
    return c if c and not c.is_deleted else None


def create_chat_keyword(db: Session, payload: ChatKeywordIn, admin_id: int) -> ChatKeywordOut:
    data: dict[str, Any] = payload.model_dump()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    c = ChatKeyword(**data)
    db.add(c)
    db.commit()
    db.refresh(c)
    return ChatKeywordOut.model_validate(c)


def update_chat_keyword(db: Session, keyword_id: int, payload: ChatKeywordIn, admin_id: int) -> ChatKeywordOut | None:
    c = get_chat_keyword(db, keyword_id)
    if not c:
        return None
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    c.updated_at = admin_id
    db.commit()
    db.refresh(c)
    return ChatKeywordOut.model_validate(c)


def delete_chat_keyword(db: Session, keyword_id: int, admin_id: int) -> bool:
    c = get_chat_keyword(db, keyword_id)
    if not c:
        return False
    c.is_deleted = 1
    c.updated_at = admin_id
    db.commit()
    return True


__all__ = ["list_chat_keywords", "get_chat_keyword", "create_chat_keyword", "update_chat_keyword", "delete_chat_keyword"]
