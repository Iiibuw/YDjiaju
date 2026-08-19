"""资讯服务层。前台公开读 + 后台 CRUD。"""
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.news import News
from app.schemas.news import NewsCreate, NewsDetail, NewsListItem


# ===== 前台 =====

def list_news_public(
    db: Session,
    *,
    category: str | None = None,
    is_top: bool | None = None,
    is_recommend: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[NewsListItem], int]:
    """前台资讯列表：仅返回已发布 + 未过期 + 未删除。"""
    q = select(News).where(
        News.is_deleted == 0,
        News.is_published == 1,
        News.is_activate == 1,
    )
    if category:
        q = q.where(News.category == category)
    if is_top is not None:
        q = q.where(News.is_top == (1 if is_top else 0))
    if is_recommend is not None:
        q = q.where(News.is_recommend == (1 if is_recommend else 0))
    # 已发布且 (无 expire_date 或 expire_date > now)
    now = datetime.utcnow()
    q = q.where((News.expire_date.is_(None)) | (News.expire_date > now))

    total_q = select(func.count()).select_from(q.subquery())
    total = db.execute(total_q).scalar() or 0

    # 排序：置顶 + 发布时间倒序
    q = q.order_by(News.is_top.desc(), News.published_date.desc(), News.sort.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).scalars().all()

    items = [NewsListItem.model_validate(r) for r in rows]
    return items, total


def get_news_detail(db: Session, news_id: int, *, increment_view: bool = True) -> NewsDetail | None:
    """前台资讯详情（含 content）。访问时 +1 浏览量。"""
    n = db.get(News, news_id)
    if not n or n.is_deleted or not n.is_published or not n.is_activate:
        return None
    if increment_view:
        n.view_count = (n.view_count or 0) + 1
        db.commit()
        db.refresh(n)
    return NewsDetail.model_validate(n)


# ===== 后台 =====

def list_news_admin(
    db: Session,
    *,
    category: str | None = None,
    is_published: bool | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[NewsDetail], int]:
    """后台资讯列表（含未发布/草稿/已软删）。"""
    q = select(News).where(News.is_deleted == 0)
    if category:
        q = q.where(News.category == category)
    if is_published is not None:
        q = q.where(News.is_published == (1 if is_published else 0))
    if keyword:
        like = f"%{keyword}%"
        q = q.where(News.title.like(like))

    total_q = select(func.count()).select_from(q.subquery())
    total = db.execute(total_q).scalar() or 0

    q = q.order_by(News.is_top.desc(), News.sort.desc(), News.created_date.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).scalars().all()
    items = [NewsDetail.model_validate(r) for r in rows]
    return items, total


def get_news_admin(db: Session, news_id: int) -> NewsDetail | None:
    """后台编辑页用（含 content）。"""
    n = db.get(News, news_id)
    if not n or n.is_deleted:
        return None
    return NewsDetail.model_validate(n)


def create_news(db: Session, payload: NewsCreate, admin_id: int) -> NewsDetail:
    """后台新建资讯。"""
    data: dict[str, Any] = payload.model_dump()
    # bool → int
    for k in ("is_published", "is_top", "is_recommend"):
        if k in data:
            data[k] = 1 if data[k] else 0
    # 默认发布时间：已发布但未填 → 用 now()
    if data.get("is_published") and not data.get("published_date"):
        data["published_date"] = datetime.utcnow()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    n = News(**data)
    db.add(n)
    db.commit()
    db.refresh(n)
    return NewsDetail.model_validate(n)


def update_news(db: Session, news_id: int, payload: NewsCreate, admin_id: int) -> NewsDetail | None:
    """后台更新资讯（PATCH 语义：仅更新显式传入的字段）。"""
    n = db.get(News, news_id)
    if not n or n.is_deleted:
        return None
    data = payload.model_dump(exclude_unset=True)
    # bool → int
    for k in ("is_published", "is_top", "is_recommend"):
        if k in data:
            data[k] = 1 if data[k] else 0
    # 首次发布（由 0→1）自动设发布时间
    if data.get("is_published") and not n.is_published and not data.get("published_date"):
        data["published_date"] = datetime.utcnow()
    for k, v in data.items():
        setattr(n, k, v)
    n.updated_at = admin_id
    db.commit()
    db.refresh(n)
    return NewsDetail.model_validate(n)


def delete_news(db: Session, news_id: int, admin_id: int) -> bool:
    """后台软删除资讯。"""
    n = db.get(News, news_id)
    if not n or n.is_deleted:
        return False
    n.is_deleted = 1
    n.updated_at = admin_id
    db.commit()
    return True


__all__ = [
    "list_news_public",
    "get_news_detail",
    "list_news_admin",
    "get_news_admin",
    "create_news",
    "update_news",
    "delete_news",
]