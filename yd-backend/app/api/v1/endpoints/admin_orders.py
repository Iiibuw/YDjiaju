"""后台订单 + 预约管理 API（需 JWT）。"""
from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentAdmin, DbDep
from app.schemas.appointment import AppointmentOut, AppointmentStatusUpdate
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.services import appointment_service, order_service

router = APIRouter(prefix="/admin", tags=["后台-订单与预约"])


@router.get("/orders", response_model=ApiResponse[dict])
def list_orders(
    db: DbDep,
    _admin: CurrentAdmin,
    status_filter: str | None = Query(None, alias="status"),
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = order_service.list_orders_admin(
        db, status_filter=status_filter, keyword=keyword, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })


@router.put("/orders/{order_id}/status", response_model=ApiResponse[OrderOut])
def update_order_status(order_id: int, payload: OrderStatusUpdate, db: DbDep, _admin: CurrentAdmin):
    o = order_service.update_order_status(db, order_id, payload.status)
    if not o:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")
    return ApiResponse(data=o, message=f"订单状态已更新为 {payload.status}")


@router.get("/appointments", response_model=ApiResponse[dict])
def list_appointments(
    db: DbDep,
    _admin: CurrentAdmin,
    status_filter: str | None = Query(None, alias="status"),
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = appointment_service.list_appointments_admin(
        db, status_filter=status_filter, keyword=keyword, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })


@router.put("/appointments/{appointment_id}/status", response_model=ApiResponse[AppointmentOut])
def update_appointment_status(appointment_id: int, payload: AppointmentStatusUpdate, db: DbDep, admin: CurrentAdmin):
    a = appointment_service.update_appointment_status(db, appointment_id, payload, admin.id)
    if not a:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    return ApiResponse(data=a, message=f"预约状态已更新为 {payload.status}")


@router.delete("/appointments/{appointment_id}", response_model=ApiResponse[dict])
def delete_appointment(appointment_id: int, db: DbDep, _admin: CurrentAdmin):
    ok = appointment_service.delete_appointment(db, appointment_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    return ApiResponse(data={"id": appointment_id}, message=f"预约 #{appointment_id} 已删除")