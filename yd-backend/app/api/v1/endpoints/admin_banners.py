"""后台轮播图管理 API（需 JWT + banner.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.banner import BannerIn, BannerOut
from app.schemas.common import ApiResponse, PageData
from app.services import banner_service

router = APIRouter(prefix="/admin/banners", tags=["后台-轮播图"])


@router.get("", response_model=ApiResponse[PageData[BannerOut]])
def list_banners(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("banner.view"))],
    keyword: str | None = Query(None),
    is_activate: int | None = Query(None, description="0/1"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = banner_service.list_banners(
        db, keyword=keyword, is_activate=is_activate, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(data=PageData[BannerOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages))


@router.get("/{banner_id}", response_model=ApiResponse[BannerOut])
def get_banner(
    banner_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("banner.view"))]
):
    b = banner_service.get_banner(db, banner_id)
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="轮播图不存在")
    return ApiResponse(data=b)


@router.post("", response_model=ApiResponse[BannerOut])
def create_banner(
    payload: BannerIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("banner.create"))]
):
    b = banner_service.create_banner(db, payload, admin.id)
    return ApiResponse(data=b, message=f"轮播图《{b.title}》创建成功")


@router.put("/{banner_id}", response_model=ApiResponse[BannerOut])
def update_banner(
    banner_id: int,
    payload: BannerIn,
    db: DbDep,
    admin: Annotated[AdminUser, Depends(require_permission("banner.edit"))],
):
    b = banner_service.update_banner(db, banner_id, payload, admin.id)
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="轮播图不存在")
    return ApiResponse(data=b, message=f"轮播图《{b.title}》已更新")


@router.delete("/{banner_id}", response_model=ApiResponse[dict])
def delete_banner(
    banner_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("banner.delete"))]
):
    ok = banner_service.delete_banner(db, banner_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="轮播图不存在")
    return ApiResponse(data={"id": banner_id}, message=f"轮播图 #{banner_id} 已删除")
