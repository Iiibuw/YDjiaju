"""前台订单 + 预约 API。"""
from fastapi import APIRouter, Depends, Query

from app.core.deps import DbDep, get_current_member
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.order import OrderCreate, OrderOut
from app.services import appointment_service, order_service

router = APIRouter(prefix="", tags=["前台-订单与预约"])


@router.post("/orders", response_model=ApiResponse[OrderOut])
def create_order(payload: OrderCreate, db: DbDep):
    """下单（M2-3：会员可传 user_id 由前端维护，简化版生成游客订单）。"""
    o = order_service.create_order(payload, db, user_id=None)
    return ApiResponse(data=o, message=f"订单 {o.order_no} 创建成功")


@router.get("/orders/me", response_model=ApiResponse[dict])
def list_my_orders(
    db: DbDep,
    member: User = Depends(get_current_member),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """我的订单（需会员）。"""
    items, total = order_service.list_my_orders(db, member.id, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })


@router.post("/appointments", response_model=ApiResponse[AppointmentOut])
def create_appointment(payload: AppointmentCreate, db: DbDep):
    """预约（游客/会员均可）。"""
    a = appointment_service.create_appointment(payload, db, user_id=None)
    return ApiResponse(data=a, message="预约成功，我们将尽快与您联系")


@router.get("/appointments/me", response_model=ApiResponse[dict])
def list_my_appointments(
    db: DbDep,
    member: User = Depends(get_current_member),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """我的预约（需会员）。"""
    items, total = appointment_service.list_my_appointments(db, member.id, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })