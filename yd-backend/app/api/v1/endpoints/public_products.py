"""GET /api/v1/public/products（列表 + 详情）。"""
from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import DbDep
from app.schemas.common import ApiResponse, PageData
from app.schemas.product import ProductDetail, ProductListItem
from app.services import product_service

router = APIRouter()


@router.get("/public/products", response_model=ApiResponse[PageData[ProductListItem]])
def list_products(
    db: DbDep,
    category_id: int | None = Query(None, description="品类 id"),
    space_id: int | None = Query(None, description="空间 id"),
    series_id: int | None = Query(None, description="系列 id"),
    keyword: str | None = Query(None, description="搜索关键词"),
    is_top: int | None = Query(None, description="是否置顶 0/1"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = product_service.list_products(
        db,
        category_id=category_id,
        space_id=space_id,
        series_id=series_id,
        keyword=keyword,
        is_top=is_top,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[ProductListItem](
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )
    )


@router.get("/public/products/{product_id}", response_model=ApiResponse[ProductDetail])
def get_product(product_id: int, db: DbDep):
    detail = product_service.get_product_detail(db, product_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在或已下架")
    return ApiResponse(data=detail)
