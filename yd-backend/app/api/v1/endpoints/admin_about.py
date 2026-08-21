"""后台关于我们管理 API（需 JWT + about.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.about import AboutSectionIn, AboutSectionOut
from app.schemas.common import ApiResponse
from app.services import about_service

router = APIRouter(prefix="/admin/about-sections", tags=["后台-关于我们"])


@router.get("", response_model=ApiResponse[list[AboutSectionOut]])
def list_about_sections(db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("about.view"))]):
    return ApiResponse(data=about_service.list_about_sections(db))


@router.get("/{section_id}", response_model=ApiResponse[AboutSectionOut])
def get_about_section(
    section_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("about.view"))]
):
    s = about_service.get_about_section(db, section_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区块不存在")
    return ApiResponse(data=s)


@router.post("", response_model=ApiResponse[AboutSectionOut])
def create_about_section(
    payload: AboutSectionIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("about.create"))]
):
    s = about_service.create_about_section(db, payload, admin.id)
    return ApiResponse(data=s, message=f"区块《{s.title}》创建成功")


@router.put("/{section_id}", response_model=ApiResponse[AboutSectionOut])
def update_about_section(
    section_id: int,
    payload: AboutSectionIn,
    db: DbDep,
    admin: Annotated[AdminUser, Depends(require_permission("about.edit"))],
):
    s = about_service.update_about_section(db, section_id, payload, admin.id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区块不存在")
    return ApiResponse(data=s, message=f"区块《{s.title}》已更新")


@router.delete("/{section_id}", response_model=ApiResponse[dict])
def delete_about_section(
    section_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("about.delete"))]
):
    ok = about_service.delete_about_section(db, section_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="区块不存在")
    return ApiResponse(data={"id": section_id}, message=f"区块 #{section_id} 已删除")
