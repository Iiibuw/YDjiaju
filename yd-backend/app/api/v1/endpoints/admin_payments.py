"""后台支付记录查询 API（只读，需 JWT + order.view 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.models.payment import Payment
from app.schemas.common import ApiResponse, PageData

router = APIRouter(prefix="/admin/payments", tags=["后台-支付记录"])

OrderViewAdmin = Annotated[AdminUser, Depends(require_permission("order.view"))]


@router.get("", response_model=ApiResponse[PageData[dict]])
def list_payments(
    db: DbDep,
    _admin: OrderViewAdmin,
    status: str | None = Query(None, description="pending/success/failed/refunded"),
    channel: str | None = Query(None, description="wechat/alipay/offline"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    q = select(Payment)
    if status:
        q = q.where(Payment.status == status)
    if channel:
        q = q.where(Payment.channel == channel)
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(Payment.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(q).scalars().all()
    total_pages = (total + page_size - 1) // page_size if total else 0
    data = [
        {
            "id": p.id,
            "order_id": p.order_id,
            "channel": p.channel,
            "transaction_id": p.transaction_id,
            "amount_cents": p.amount_cents,
            "status": p.status,
            "paid_date": p.paid_date.isoformat() if p.paid_date else None,
            "created_date": p.created_date.isoformat() if p.created_date else None,
        }
        for p in rows
    ]
    return ApiResponse(data=PageData[dict](items=data, total=total, page=page, page_size=page_size, total_pages=total_pages))
