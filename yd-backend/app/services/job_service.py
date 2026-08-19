"""招聘服务层。前台公开读 + 后台 CRUD + 投递。"""
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.job_application import JobApplication
from app.schemas.job import JobApplicationCreate, JobApplicationOut, JobCreate, JobDetail, JobListItem


# ===== 前台 =====

def list_jobs_public(
    db: Session,
    *,
    category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[JobListItem], int]:
    """前台岗位列表：未过期 + 启用 + 未删。"""
    q = select(Job).where(Job.is_deleted == 0, Job.is_activate == 1)
    if category:
        q = q.where(Job.category == category)
    now = datetime.utcnow()
    q = q.where((Job.expire_date.is_(None)) | (Job.expire_date > now))
    total_q = select(func.count()).select_from(q.subquery())
    total = db.execute(total_q).scalar() or 0
    q = q.order_by(Job.publish_date.desc(), Job.created_date.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).scalars().all()
    items = [JobListItem.model_validate(r) for r in rows]
    return items, total


def get_job_detail(db: Session, job_id: int) -> JobDetail | None:
    """前台岗位详情。"""
    j = db.get(Job, job_id)
    if not j or j.is_deleted or not j.is_activate:
        return None
    if j.expire_date and j.expire_date < datetime.utcnow():
        return None
    return JobDetail.model_validate(j)


def apply_job(db: Session, payload: JobApplicationCreate) -> JobApplicationOut:
    """前台投递岗位（公开）。"""
    job = db.get(Job, payload.job_id)
    if not job or job.is_deleted or not job.is_activate:
        raise ValueError("岗位不存在或已下架")
    if job.expire_date and job.expire_date < datetime.utcnow():
        raise ValueError("岗位已截止招聘")

    app_obj = JobApplication(
        job_id=payload.job_id,
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        region_code=payload.region_code,
        resume_url=payload.resume_url,
        stage="applied",
        applied_date=datetime.utcnow(),
    )
    db.add(app_obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("您已投递过此岗位，请勿重复")
    db.refresh(app_obj)
    return JobApplicationOut.model_validate(app_obj)


# ===== 后台 =====

def list_jobs_admin(
    db: Session,
    *,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[JobDetail], int]:
    """后台岗位列表。"""
    q = select(Job).where(Job.is_deleted == 0)
    if category:
        q = q.where(Job.category == category)
    if keyword:
        q = q.where(Job.title.like(f"%{keyword}%"))
    total_q = select(func.count()).select_from(q.subquery())
    total = db.execute(total_q).scalar() or 0
    q = q.order_by(Job.publish_date.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).scalars().all()
    items = [JobDetail.model_validate(r) for r in rows]
    return items, total


def create_job(db: Session, payload: JobCreate, admin_id: int) -> JobDetail:
    data: dict[str, Any] = payload.model_dump()
    data["is_activate"] = 1 if data.get("is_activate") else 0
    if not data.get("publish_date"):
        data["publish_date"] = datetime.utcnow()
    data["created_at"] = admin_id
    data["updated_at"] = admin_id
    j = Job(**data)
    db.add(j)
    db.commit()
    db.refresh(j)
    return JobDetail.model_validate(j)


def update_job(db: Session, job_id: int, payload: JobCreate, admin_id: int) -> JobDetail | None:
    j = db.get(Job, job_id)
    if not j or j.is_deleted:
        return None
    # PATCH 语义：只更新显式传入的字段（避免 publish_date=None 触发 NOT NULL）
    data = payload.model_dump(exclude_unset=True)
    if "is_activate" in data:
        data["is_activate"] = 1 if data["is_activate"] else 0
    for k, v in data.items():
        setattr(j, k, v)
    j.updated_at = admin_id
    db.commit()
    db.refresh(j)
    return JobDetail.model_validate(j)


def delete_job(db: Session, job_id: int, admin_id: int) -> bool:
    j = db.get(Job, job_id)
    if not j or j.is_deleted:
        return False
    j.is_deleted = 1
    j.updated_at = admin_id
    db.commit()
    return True


def list_applications_admin(
    db: Session,
    *,
    job_id: int | None = None,
    stage: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[JobApplicationOut], int]:
    """后台投递记录列表（含 job_title 关联查询）。"""
    q = select(JobApplication, Job.title).outerjoin(Job, JobApplication.job_id == Job.id)
    if job_id:
        q = q.where(JobApplication.job_id == job_id)
    if stage:
        q = q.where(JobApplication.stage == stage)
    total_q = select(func.count()).select_from(q.subquery())
    total = db.execute(total_q).scalar() or 0
    q = q.order_by(JobApplication.applied_date.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).all()

    items: list[JobApplicationOut] = []
    for app_obj, job_title in rows:
        out = JobApplicationOut.model_validate(app_obj)
        out.job_title = job_title
        items.append(out)
    return items, total


__all__ = [
    "list_jobs_public",
    "get_job_detail",
    "apply_job",
    "list_jobs_admin",
    "create_job",
    "update_job",
    "delete_job",
    "list_applications_admin",
]