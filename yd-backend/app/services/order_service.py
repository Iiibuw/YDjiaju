"""订单服务层：会员下单 + 我的订单 + 后台管理。"""
import time

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderItemOut, OrderOut


def _gen_order_no() -> str:
    """生成订单号：YD + 时间戳 + 随机。"""
    return f"YD{int(time.time() * 1000)}{int(time.time() % 1000):03d}"


def create_order(payload: OrderCreate, db: Session, user_id: int | None) -> OrderOut:
    """下单（M2-3 简化：直接生成 pending 订单，支付二期待接）。"""
    # 校验商品 + 计算金额
    order = Order(
        order_no=_gen_order_no(),
        user_id=user_id,
        receiver_name=payload.receiver_name,
        receiver_phone=payload.receiver_phone,
        receiver_address=payload.receiver_address,
        remark=payload.remark,
        status="pending",
        total_cents=0,
        shipping_cents=0,
        discount_cents=0,
        final_cents=0,
    )
    db.add(order)
    db.flush()

    items_out: list[OrderItemOut] = []
    total = 0
    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product or product.status != "on_sale" or product.is_deleted:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"产品 #{item.product_id} 不存在或已下架")
        price = (product.min_price_cents or 0) if product.max_price_cents is None else (product.min_price_cents or product.max_price_cents or 0)
        subtotal = price * item.quantity
        total += subtotal
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            cover_url=product.cover_url,
            price_cents=price,
            quantity=item.quantity,
            subtotal_cents=subtotal,
        )
        db.add(oi)
        db.flush()
        items_out.append(OrderItemOut.model_validate(oi))

    order.total_cents = total
    order.final_cents = total
    db.commit()
    db.refresh(order)

    out = OrderOut.model_validate(order)
    out.items = items_out
    return out


def list_my_orders(db: Session, user_id: int, page: int = 1, page_size: int = 20) -> tuple[list[OrderOut], int]:
    q = select(Order).where(Order.user_id == user_id)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    result: list[OrderOut] = []
    for o in rows:
        out = OrderOut.model_validate(o)
        out.items = [OrderItemOut.model_validate(i) for i in db.scalars(
            select(OrderItem).where(OrderItem.order_id == o.id)
        ).all()]
        result.append(out)
    return result, total


def get_order(db: Session, order_id: int, user_id: int | None = None) -> OrderOut | None:
    o = db.get(Order, order_id)
    if not o:
        return None
    if user_id is not None and o.user_id != user_id:
        return None
    out = OrderOut.model_validate(o)
    out.items = [OrderItemOut.model_validate(i) for i in db.scalars(
        select(OrderItem).where(OrderItem.order_id == o.id)
    ).all()]
    return out


def list_orders_admin(
    db: Session, *, status_filter: str | None = None, keyword: str | None = None,
    page: int = 1, page_size: int = 20,
) -> tuple[list[OrderOut], int]:
    q = select(Order)
    if status_filter:
        q = q.where(Order.status == status_filter)
    if keyword:
        like = f"%{keyword}%"
        q = q.where((Order.order_no.like(like)) | (Order.receiver_name.like(like)) | (Order.receiver_phone.like(like)))
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    result: list[OrderOut] = []
    for o in rows:
        out = OrderOut.model_validate(o)
        out.items = [OrderItemOut.model_validate(i) for i in db.scalars(
            select(OrderItem).where(OrderItem.order_id == o.id)
        ).all()]
        result.append(out)
    return result, total


def update_order_status(db: Session, order_id: int, new_status: str) -> OrderOut | None:
    """状态流转：pending→paid→shipped→completed；任意状态→closed。"""
    from datetime import datetime

    o = db.get(Order, order_id)
    if not o:
        return None
    valid = {"pending", "paid", "shipped", "completed", "closed"}
    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"非法状态：{new_status}")
    o.status = new_status
    now = datetime.utcnow()
    if new_status == "paid":
        o.paid_date = now
    elif new_status == "shipped":
        o.shipped_date = now
    elif new_status == "completed":
        o.completed_date = now
    elif new_status == "closed":
        o.closed_date = now
    db.commit()
    db.refresh(o)
    out = OrderOut.model_validate(o)
    out.items = [OrderItemOut.model_validate(i) for i in db.scalars(
        select(OrderItem).where(OrderItem.order_id == o.id)
    ).all()]
    return out


__all__ = [
    "create_order", "list_my_orders", "get_order",
    "list_orders_admin", "update_order_status",
]