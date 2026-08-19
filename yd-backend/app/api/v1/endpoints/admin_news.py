"""后台资讯管理 API（需 JWT）。"""
from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentAdmin, DbDep
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.news import NewsCreate, NewsDetail, NewsListOut
from app.services import news_service

router = APIRouter(prefix="/admin/news", tags=["后台-资讯"])


@router.get("", response_model=ApiResponse[NewsListOut])
def list_news(
    db: DbDep,
    _admin: CurrentAdmin,
    category: str | None = None,
    is_published: bool | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """后台：资讯列表（含草稿/已发布/已软删过滤）。"""
    items, total = news_service.list_news_admin(
        db, category=category, is_published=is_published, keyword=keyword,
        page=page, page_size=page_size,
    )
    return ApiResponse(
        data=NewsListOut(
            items=[NewsDetail.model_validate(i) for i in items],
            total=total, page=page, page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size else 0,
            meta=PaginationMeta(
                total=total, page=page, page_size=page_size,
                total_pages=(total + page_size - 1) // page_size if page_size else 0,
            ).model_dump(),
        )
    )


@router.get("/{news_id}", response_model=ApiResponse[NewsDetail])
def get_news(news_id: int, db: DbDep, _admin: CurrentAdmin):
    """后台：资讯编辑页（含 content）。"""
    n = news_service.get_news_admin(db, news_id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在")
    return ApiResponse(data=n)


@router.post("", response_model=ApiResponse[NewsDetail])
def create_news(payload: NewsCreate, db: DbDep, admin: CurrentAdmin):
    """后台：新建资讯。"""
    n = news_service.create_news(db, payload, admin.id)
    return ApiResponse(data=n, message=f"资讯《{n.title}》创建成功")


@router.put("/{news_id}", response_model=ApiResponse[NewsDetail])
def update_news(news_id: int, payload: NewsCreate, db: DbDep, admin: CurrentAdmin):
    """后台：更新资讯。"""
    n = news_service.update_news(db, news_id, payload, admin.id)
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在")
    return ApiResponse(data=n, message=f"资讯《{n.title}》已更新")


@router.delete("/{news_id}", response_model=ApiResponse[dict])
def delete_news(news_id: int, db: DbDep, admin: CurrentAdmin):
    """后台：软删除资讯。"""
    ok = news_service.delete_news(db, news_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="资讯不存在")
    return ApiResponse(data={"id": news_id}, message=f"资讯 #{news_id} 已删除")