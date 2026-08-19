"""前台招聘 API（公开）。"""
from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import DbDep
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationOut,
    JobDetail,
    JobListItem,
)
from app.services import job_service

router = APIRouter(prefix="/public/jobs", tags=["前台-招聘"])


@router.get("", response_model=ApiResponse[dict])
def list_jobs(
    db: DbDep,
    category: str | None = Query(None, description="social/campus"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """前台：岗位列表。"""
    items, total = job_service.list_jobs_public(
        db, category=category, page=page, page_size=page_size
    )
    return ApiResponse(
        data={
            "items": [JobListItem.model_validate(i) for i in items],
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


@router.get("/{job_id}", response_model=ApiResponse[JobDetail])
def get_job_detail(job_id: int, db: DbDep):
    """前台：岗位详情。"""
    j = job_service.get_job_detail(db, job_id)
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="岗位不存在或已下架")
    return ApiResponse(data=j)


@router.post("/apply", response_model=ApiResponse[JobApplicationOut])
def apply_job(payload: JobApplicationCreate, db: DbDep):
    """前台：投递岗位（公开 API，无须登录）。"""
    try:
        out = job_service.apply_job(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ApiResponse(data=out, message="投递成功，我们会在 3 个工作日内与您联系")