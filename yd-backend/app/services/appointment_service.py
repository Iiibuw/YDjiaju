"""预约服务层：前台提交 + 我的预约 + 后台管理。"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate


def create_appointment(payload: AppointmentCreate, db: Session, user_id: int | None) -> AppointmentOut:
    a = Appointment(
        user_id=user_id,
        type=payload.type,
        name=payload.name,
        phone=payload.phone,
        preferred_date=payload.preferred_date,
        message=payload.message,
        source_page=payload.source_page,
        status="pending",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return AppointmentOut.model_validate(a)


def list_my_appointments(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> tuple[list[AppointmentOut], int]:
    q = select(Appointment).where(Appointment.user_id == user_id)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Appointment.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    return [AppointmentOut.model_validate(a) for a in rows], total


def list_appointments_admin(
    db: Session, *, status_filter: str | None = None, keyword: str | None = None,
    page: int = 1, page_size: int = 20,
) -> tuple[list[AppointmentOut], int]:
    q = select(Appointment)
    if status_filter:
        q = q.where(Appointment.status == status_filter)
    if keyword:
        like = f"%{keyword}%"
        q = q.where((Appointment.name.like(like)) | (Appointment.phone.like(like)))
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Appointment.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    return [AppointmentOut.model_validate(a) for a in rows], total


def update_appointment_status(db: Session, appointment_id: int, payload: AppointmentStatusUpdate, admin_id: int) -> AppointmentOut | None:
    a = db.get(Appointment, appointment_id)
    if not a:
        return None
    valid = {"pending", "following", "converted", "invalid"}
    if payload.status not in valid:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=f"非法状态：{payload.status}")
    a.status = payload.status
    if payload.follow_note:
        a.follow_note = payload.follow_note
    a.followed_date = datetime.utcnow()
    a.assignee_id = admin_id
    db.commit()
    db.refresh(a)
    return AppointmentOut.model_validate(a)


def delete_appointment(db: Session, appointment_id: int) -> bool:
    a = db.get(Appointment, appointment_id)
    if not a:
        return False
    a.is_activate = 0
    db.commit()
    return True


__all__ = [
    "create_appointment", "list_my_appointments",
    "list_appointments_admin", "update_appointment_status", "delete_appointment",
]