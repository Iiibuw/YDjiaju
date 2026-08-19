"""案例服务层。前台公开读 + 后台 CRUD。"""
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.category import Category
from app.schemas.case import CaseCreate, CaseDetail, CaseListItem


# ===== 公共读（前台） =====

def list_cases(
    db: Session,
    *,
    category_id: int | None = None,
    is_top: bool | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[CaseListItem], int]:
    """前台案例列表：已激活 + 未删除；按发布时间倒序。"""
    q = select(Case).where(Case.is_deleted == 0, Case.is_activate == 1)
    if category_id:
        q = q.where(Case.category_id == category_id)
    if is_top is not None:
        # M2-2 简化：用 sort=999 表示置顶
        q = q.where(Case.sort == 999 if is_top else Case.sort < 999)
    if keyword:
        q = q.where(Case.title.like(f"%{keyword}%"))

    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Case.sort.desc(), Case.published_date.desc(), Case.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()

    items = [CaseListItem.model_validate(c) for c in rows]
    return items, total


def get_case_detail(db: Session, case_id: int) -> CaseDetail | None:
    """前台案例详情（浏览量自增 + category join）。"""
    c = db.get(Case, case_id)
    if not c or c.is_deleted or not c.is_activate:
        return None
    c.view_count = (c.view_count or 0) + 1
    db.commit()
    db.refresh(c)

    # category join（轻量查表，避免 N+1）
    cat_dict = None
    if c.category_id:
        cat = db.get(Category, c.category_id)
        if cat:
            cat_dict = {"id": cat.id, "name": cat.name}

    detail = CaseDetail.model_validate(c)
    detail.category = cat_dict
    detail.images = [c.cover_url] if c.cover_url else []
    return detail


# ===== 后台 =====

def list_cases_admin(
    db: Session,
    *,
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[CaseDetail], int]:
    """后台：含已软删/已禁用。"""
    q = select(Case)
    if keyword:
        q = q.where(Case.title.like(f"%{keyword}%"))
    if category_id:
        q = q.where(Case.category_id == category_id)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Case.sort.desc(), Case.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    return [CaseDetail.model_validate(c) for c in rows], total


def get_case_admin(db: Session, case_id: int) -> CaseDetail | None:
    """后台：包含已软删（admin 全可见），返回 None 表示案例不存在（未创建）。"""
    c = db.get(Case, case_id)
    if not c:
        return None
    detail = CaseDetail.model_validate(c)
    if c.category_id:
        cat = db.get(Category, c.category_id)
        if cat:
            detail.category = {"id": cat.id, "name": cat.name}
    detail.images = [c.cover_url] if c.cover_url else []
    return detail


def create_case(db: Session, payload: CaseCreate, admin_id: int) -> CaseDetail:
    """新建案例。"""
    c = Case(
        title=payload.title,
        category_id=payload.category_id,
        cover_url=payload.cover_url,
        style=payload.style,
        area=payload.area,
        description=payload.description,
        published_date=payload.published_date or datetime.utcnow(),
        sort=payload.sort,
        view_count=0,
        created_at=admin_id,
        updated_at=admin_id,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return CaseDetail.model_validate(c)


def update_case(db: Session, case_id: int, payload: CaseCreate, admin_id: int) -> CaseDetail | None:
    """更新案例（PATCH 语义）。"""
    c = db.get(Case, case_id)
    if not c or c.is_deleted:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(c, k, v)
    c.updated_at = admin_id
    db.commit()
    db.refresh(c)
    return CaseDetail.model_validate(c)


def delete_case(db: Session, case_id: int, admin_id: int) -> bool:
    """软删除案例。"""
    c = db.get(Case, case_id)
    if not c or c.is_deleted:
        return False
    c.is_deleted = 1
    c.deleted_at = datetime.utcnow()
    c.updated_at = admin_id
    db.commit()
    return True


__all__ = [
    "list_cases", "get_case_detail",
    "list_cases_admin", "get_case_admin",
    "create_case", "update_case", "delete_case",
]