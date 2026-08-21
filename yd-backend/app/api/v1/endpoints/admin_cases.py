"""后台案例管理 API（需 JWT）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.case import CaseCreate, CaseDetail, CaseListItem
from app.schemas.common import ApiResponse, PaginationMeta
from app.services import case_service

router = APIRouter(prefix="/admin/cases", tags=["后台-案例"])


@router.get("", response_model=ApiResponse[dict])
def list_cases(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("case.view"))],
    keyword: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """后台：案例列表（含草稿/已软删）。"""
    items, total = case_service.list_cases_admin(
        db, keyword=keyword, category_id=category_id, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": [CaseDetail.model_validate(i) for i in items],
        "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(
            total=total, page=page, page_size=page_size, total_pages=total_pages
        ).model_dump(),
    })


@router.get("/{case_id}", response_model=ApiResponse[CaseDetail])
def get_case(case_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("case.view"))]):
    c = case_service.get_case_admin(db, case_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="案例不存在")
    return ApiResponse(data=c)


@router.post("", response_model=ApiResponse[CaseDetail])
def create_case(payload: CaseCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("case.create"))]):
    c = case_service.create_case(db, payload, admin.id)
    return ApiResponse(data=c, message=f"案例《{c.title}》已创建")


@router.put("/{case_id}", response_model=ApiResponse[CaseDetail])
def update_case(case_id: int, payload: CaseCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("case.edit"))]):
    c = case_service.update_case(db, case_id, payload, admin.id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="案例不存在")
    return ApiResponse(data=c, message=f"案例《{c.title}》已更新")


@router.delete("/{case_id}", response_model=ApiResponse[dict])
def delete_case(case_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("case.delete"))]):
    ok = case_service.delete_case(db, case_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="案例不存在")
    return ApiResponse(data={"id": case_id}, message=f"案例 #{case_id} 已删除")