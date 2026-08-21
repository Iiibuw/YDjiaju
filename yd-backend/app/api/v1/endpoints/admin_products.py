"""后台产品 CRUD（admin/auth + product M1）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PageData
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import product_service

router = APIRouter()


@router.get("/admin/products", response_model=ApiResponse[PageData[dict]])
def list_products(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("product.view"))],
    keyword: str | None = Query(None),
    status_filter: str | None = Query(None, description="draft/on_sale/off_sale"),
    category_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = product_service.list_admin_products(
        db, keyword=keyword, status_filter=status_filter, category_id=category_id, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[dict](
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )
    )


@router.post("/admin/products", response_model=ApiResponse[dict])
def create_product(payload: ProductCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("product.create"))]):
    p = product_service.create_product(db, payload, admin.id)
    return ApiResponse(data=product_service.to_admin_dict(p), message=f"产品 {p.name} 创建成功")


@router.get("/admin/products/{product_id}", response_model=ApiResponse[dict])
def get_product(product_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("product.view"))]):
    """后台产品详情(完整 ORM,含 status=on_sale=off_sale=draft;支持 style/space_id/series_id 等全部字段)。"""
    p = product_service.get_admin_product(db, product_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return ApiResponse(data=product_service.to_admin_dict(p))


@router.put("/admin/products/{product_id}", response_model=ApiResponse[dict])
def update_product(product_id: int, payload: ProductUpdate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("product.edit"))]):
    try:
        p = product_service.update_product(db, product_id, payload, admin.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return ApiResponse(data=product_service.to_admin_dict(p), message=f"产品 #{product_id} 已更新")


@router.delete("/admin/products/{product_id}", response_model=ApiResponse[dict])
def delete_product(product_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("product.delete"))]):
    ok = product_service.delete_product(db, product_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")
    return ApiResponse(data={"id": product_id}, message="已删除（软删除）")
