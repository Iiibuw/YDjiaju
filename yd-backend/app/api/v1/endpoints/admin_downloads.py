"""后台下载中心管理 API（需 JWT + download.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PageData
from app.schemas.download import DownloadIn, DownloadOut
from app.services import download_service

router = APIRouter(prefix="/admin/downloads", tags=["后台-下载中心"])


@router.get("", response_model=ApiResponse[PageData[DownloadOut]])
def list_downloads(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("download.view"))],
    category: str | None = Query(None, description="catalog/manual/cad/other"),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = download_service.list_downloads(db, category=category, keyword=keyword, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[DownloadOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
    )


@router.get("/{download_id}", response_model=ApiResponse[DownloadOut])
def get_download(
    download_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("download.view"))]
):
    d = download_service.get_download(db, download_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="下载资料不存在")
    return ApiResponse(data=d)


@router.post("", response_model=ApiResponse[DownloadOut])
def create_download(
    payload: DownloadIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("download.create"))]
):
    d = download_service.create_download(db, payload, admin.id)
    return ApiResponse(data=d, message=f"资料《{d.title}》创建成功")


@router.put("/{download_id}", response_model=ApiResponse[DownloadOut])
def update_download(
    download_id: int,
    payload: DownloadIn,
    db: DbDep,
    admin: Annotated[AdminUser, Depends(require_permission("download.edit"))],
):
    d = download_service.update_download(db, download_id, payload, admin.id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="下载资料不存在")
    return ApiResponse(data=d, message=f"资料《{d.title}》已更新")


@router.delete("/{download_id}", response_model=ApiResponse[dict])
def delete_download(
    download_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("download.delete"))]
):
    ok = download_service.delete_download(db, download_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="下载资料不存在")
    return ApiResponse(data={"id": download_id}, message=f"资料 #{download_id} 已删除")
