"""前台轮播图 API（公开）：启用中 + 时间窗内，按 sort 排序。"""
from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import or_, select

from app.core.deps import DbDep
from app.models.banner import Banner
from app.schemas.banner import BannerOut
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/public/banners", tags=["前台-轮播"])


@router.get("", response_model=ApiResponse[list[BannerOut]])
def list_banners(db: DbDep):
    """首页轮播：is_activate=1 且在 [start_date, end_date] 时间窗内。"""
    now = datetime.utcnow()
    q = (
        select(Banner)
        .where(
            Banner.is_deleted == 0,
            Banner.is_activate == 1,
            or_(Banner.start_date.is_(None), Banner.start_date <= now),
            or_(Banner.end_date.is_(None), Banner.end_date >= now),
        )
        .order_by(Banner.sort, Banner.id)
    )
    items = [BannerOut.model_validate(b) for b in db.execute(q).scalars().all()]
    return ApiResponse(data=items)
