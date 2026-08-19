"""前台资讯 API（公开）。"""
from fastapi import APIRouter, Query

from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.news import NewsDetail as NewsDetailSchema, NewsListItem
from app.services import news_service
from app.core.deps import DbDep

router = APIRouter(prefix="/public/news", tags=["前台-资讯"])


@router.get("", response_model=ApiResponse[dict])
def list_news(
    db: DbDep,
    category: str | None = Query(None, description="company/industry"),
    is_top: bool | None = Query(None),
    is_recommend: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """前台：已发布资讯列表。"""
    items, total = news_service.list_news_public(
        db, category=category, is_top=is_top, is_recommend=is_recommend,
        page=page, page_size=page_size,
    )
    return ApiResponse(
        data={
            "items": [NewsListItem.model_validate(i) for i in items],
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


@router.get("/{news_id}", response_model=ApiResponse[NewsDetailSchema])
def get_news_detail(news_id: int, db: DbDep):
    """前台：资讯详情（自动 +1 浏览量）。"""
    n = news_service.get_news_detail(db, news_id)
    if not n:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在或已下线")
    return ApiResponse(data=n)