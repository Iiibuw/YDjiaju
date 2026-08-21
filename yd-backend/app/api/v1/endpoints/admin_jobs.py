"""后台招聘管理 API（需 JWT）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.job import (
    JobApplicationListOut,
    JobApplicationOut,
    JobCreate,
    JobDetail,
    JobListItem,
    JobListOut,
)
from app.services import job_service

router = APIRouter(prefix="/admin/jobs", tags=["后台-招聘"])


@router.get("", response_model=ApiResponse[JobListOut])
def list_jobs(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("job.view"))],
    category: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """后台：岗位列表。"""
    items, total = job_service.list_jobs_admin(
        db, category=category, keyword=keyword, page=page, page_size=page_size
    )
    return ApiResponse(
        data=JobListOut(
            items=[JobListItem.model_validate(i) for i in items],
            total=total, page=page, page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size else 0,
            meta=PaginationMeta(
                total=total, page=page, page_size=page_size,
                total_pages=(total + page_size - 1) // page_size if page_size else 0,
            ).model_dump(),
        )
    )


@router.post("", response_model=ApiResponse[JobDetail])
def create_job(payload: JobCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("job.edit"))]):
    """后台：新建岗位。"""
    j = job_service.create_job(db, payload, admin.id)
    return ApiResponse(data=j, message=f"岗位《{j.title}》创建成功")


@router.put("/{job_id}", response_model=ApiResponse[JobDetail])
def update_job(job_id: int, payload: JobCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("job.edit"))]):
    """后台：更新岗位。"""
    j = job_service.update_job(db, job_id, payload, admin.id)
    if not j:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="岗位不存在")
    return ApiResponse(data=j, message=f"岗位《{j.title}》已更新")


@router.delete("/{job_id}", response_model=ApiResponse[dict])
def delete_job(job_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("job.edit"))]):
    """后台：软删除岗位。"""
    ok = job_service.delete_job(db, job_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="岗位不存在")
    return ApiResponse(data={"id": job_id}, message=f"岗位 #{job_id} 已删除")


@router.get("/applications", response_model=ApiResponse[JobApplicationListOut])
def list_applications(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("job.view"))],
    job_id: int | None = Query(None, description="按岗位过滤"),
    stage: str | None = Query(None, description="applied/screening/interview/offer/rejected"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """后台：投递记录列表（含 job_title 关联）。"""
    items, total = job_service.list_applications_admin(
        db, job_id=job_id, stage=stage, page=page, page_size=page_size
    )
    return ApiResponse(
        data=JobApplicationListOut(
            items=items, total=total, page=page, page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if page_size else 0,
            meta=PaginationMeta(
                total=total, page=page, page_size=page_size,
                total_pages=(total + page_size - 1) // page_size if page_size else 0,
            ).model_dump(),
        )
    )