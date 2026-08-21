"""下载中心服务层（后台）。"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.download import Download
from app.schemas.download import DownloadIn, DownloadOut


def list_downloads(
    db: Session,
    *,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[DownloadOut], int]:
    q = select(Download).where(Download.is_deleted == 0)
    if category:
        q = q.where(Download.category == category)
    if keyword:
        q = q.where(Download.title.like(f"%{keyword}%"))
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(Download.sort, Download.id)
    q = q.offset((page - 1) * page_size).limit(page_size)
    items = [DownloadOut.model_validate(r) for r in db.execute(q).scalars().all()]
    return items, total


def get_download(db: Session, download_id: int) -> Download | None:
    return db.get(Download, download_id)


def create_download(db: Session, payload: DownloadIn, admin_id: int) -> DownloadOut:
    data: dict[str, Any] = payload.model_dump()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    d = Download(**data)
    db.add(d)
    db.commit()
    db.refresh(d)
    return DownloadOut.model_validate(d)


def update_download(db: Session, download_id: int, payload: DownloadIn, admin_id: int) -> DownloadOut | None:
    d = db.get(Download, download_id)
    if not d:
        return None
    for k, v in payload.model_dump().items():
        setattr(d, k, v)
    d.updated_at = admin_id
    db.commit()
    db.refresh(d)
    return DownloadOut.model_validate(d)


def delete_download(db: Session, download_id: int, admin_id: int) -> bool:
    """软删除。"""
    d = db.get(Download, download_id)
    if not d or d.is_deleted:
        return False
    d.is_deleted = 1
    d.updated_at = admin_id
    db.commit()
    return True


__all__ = ["list_downloads", "get_download", "create_download", "update_download", "delete_download"]
