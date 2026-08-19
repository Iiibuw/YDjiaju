"""案例服务层。"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.category import Category
from app.schemas.case import CaseDetail, CaseListItem


def list_cases(
    db: Session,
    *,
    category_id: int | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[CaseListItem], int]:
    """前台案例列表。"""
    q = select(Case).where(Case.is_deleted == 0, Case.is_activate == 1)
    if category_id:
        q = q.where(Case.category_id == category_id)
    if keyword:
        q = q.where(Case.title.like(f"%{keyword}%"))

    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Case.published_date.desc(), Case.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()

    items: list[CaseListItem] = []
    for c in rows:
        items.append(
            CaseListItem(
                id=c.id,
                title=c.title,
                cover_url=c.cover_url,
                style=c.style,
                area=c.area,
                published_date=c.published_date.isoformat() if c.published_date else "",
                view_count=c.view_count,
                category_id=c.category_id,
            )
        )
    return items, total


def get_case_detail(db: Session, case_id: int) -> CaseDetail | None:
    """前台案例详情（M1 简化：images 暂空，M2 接 case_images 表）。"""
    c = db.get(Case, case_id)
    if not c or c.is_deleted or not c.is_activate:
        return None

    # 浏览量 +1
    c.view_count = (c.view_count or 0) + 1
    db.commit()

    def _cat(cid: int | None) -> dict | None:
        if not cid:
            return None
        cat = db.get(Category, cid)
        return {"id": cat.id, "name": cat.name} if cat else None

    return CaseDetail(
        id=c.id,
        title=c.title,
        cover_url=c.cover_url,
        style=c.style,
        area=c.area,
        description=c.description,
        published_date=c.published_date.isoformat() if c.published_date else "",
        view_count=c.view_count,
        category=_cat(c.category_id),
        images=[c.cover_url] if c.cover_url else [],  # M1 简化：用 cover 作主图
    )


__all__ = ["list_cases", "get_case_detail"]
