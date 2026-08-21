"""后台站点配置管理 API（需 JWT + system.config 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PageData
from app.schemas.site_config import SiteConfigIn, SiteConfigOut
from app.services import site_config_service

router = APIRouter(prefix="/admin/site-configs", tags=["后台-站点配置"])


@router.get("", response_model=ApiResponse[PageData[SiteConfigOut]])
def list_site_configs(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("system.config"))],
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    items, total = site_config_service.list_site_configs(db, category=category, keyword=keyword, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[SiteConfigOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
    )


@router.get("/key/{config_key}", response_model=ApiResponse[SiteConfigOut])
def get_site_config(
    config_key: str, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("system.config"))]
):
    cfg = site_config_service.get_by_key(db, config_key)
    if not cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="配置不存在")
    return ApiResponse(data=cfg)


@router.post("", response_model=ApiResponse[SiteConfigOut])
def upsert_site_config(
    payload: SiteConfigIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("system.config"))]
):
    cfg = site_config_service.upsert_site_config(db, payload, admin.id)
    return ApiResponse(data=cfg, message=f"配置 {cfg.config_key} 已保存")
