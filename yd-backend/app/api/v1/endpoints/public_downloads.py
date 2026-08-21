"""前台下载中心 API（公开）：启用中的资料列表。"""
from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.core.deps import DbDep
from app.models.download import Download
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.download import DownloadOut

router = APIRouter(prefix="/public/downloads", tags=["前台-下载中心"])


@router.get("", response_model=ApiResponse[dict])
def list_downloads(
    db: DbDep,
    category: str | None = Query(None, description="catalog/manual/cad/other"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    q = select(Download).where(Download.is_deleted == 0, Download.is_activate == 1)
    if category:
        q = q.where(Download.category == category)
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(Download.sort, Download.id).offset((page - 1) * page_size).limit(page_size)
    items = [DownloadOut.model_validate(d) for d in db.execute(q).scalars().all()]
    return ApiResponse(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size else 0,
            "meta": PaginationMeta(
                total=total, page=page, page_size=page_size,
                total_pages=(total + page_size - 1) // page_size if page_size else 0,
            ).model_dump(),
        }
    )
