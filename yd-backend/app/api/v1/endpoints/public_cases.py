"""GET /api/v1/public/cases。"""
from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import DbDep
from app.schemas.case import CaseDetail, CaseListItem
from app.schemas.common import ApiResponse, PageData
from app.services import case_service

router = APIRouter()


@router.get("/public/cases", response_model=ApiResponse[PageData[CaseListItem]])
def list_cases(
    db: DbDep,
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = case_service.list_cases(db, category_id=category_id, keyword=keyword, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[CaseListItem](
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )
    )


@router.get("/public/cases/{case_id}", response_model=ApiResponse[CaseDetail])
def get_case(case_id: int, db: DbDep):
    detail = case_service.get_case_detail(db, case_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="案例不存在")
    return ApiResponse(data=detail)
