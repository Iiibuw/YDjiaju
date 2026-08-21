"""轮播图服务层（后台）。"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.banner import Banner
from app.schemas.banner import BannerIn, BannerOut


def list_banners(
    db: Session,
    *,
    keyword: str | None = None,
    is_activate: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BannerOut], int]:
    q = select(Banner).where(Banner.is_deleted == 0)
    if is_activate is not None:
        q = q.where(Banner.is_activate == is_activate)
    if keyword:
        q = q.where(Banner.title.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(Banner.sort, Banner.id)
    q = q.offset((page - 1) * page_size).limit(page_size)
    items = [BannerOut.model_validate(r) for r in db.execute(q).scalars().all()]
    return items, total


def get_banner(db: Session, banner_id: int) -> Banner | None:
    return db.get(Banner, banner_id)


def create_banner(db: Session, payload: BannerIn, admin_id: int) -> BannerOut:
    data: dict[str, Any] = payload.model_dump()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    b = Banner(**data)
    db.add(b)
    db.commit()
    db.refresh(b)
    return BannerOut.model_validate(b)


def update_banner(db: Session, banner_id: int, payload: BannerIn, admin_id: int) -> BannerOut | None:
    b = db.get(Banner, banner_id)
    if not b:
        return None
    for k, v in payload.model_dump().items():
        setattr(b, k, v)
    b.updated_at = admin_id
    db.commit()
    db.refresh(b)
    return BannerOut.model_validate(b)


def delete_banner(db: Session, banner_id: int, admin_id: int) -> bool:
    """软删除。"""
    b = db.get(Banner, banner_id)
    if not b or b.is_deleted:
        return False
    b.is_deleted = 1
    b.updated_at = admin_id
    db.commit()
    return True


__all__ = ["list_banners", "get_banner", "create_banner", "update_banner", "delete_banner"]
