"""后台仪表盘统计 API（需 JWT + dashboard.view 权限）。"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.models.appointment import Appointment
from app.models.message import Message
from app.models.news import News
from app.models.order import Order
from app.models.product import Product
from app.models.stats_visit import StatsVisit
from app.models.user import User
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/admin/dashboard", tags=["后台-仪表盘"])

DashboardAdmin = Annotated[AdminUser, Depends(require_permission("dashboard.view"))]


@router.get("/stats", response_model=ApiResponse[dict])
def dashboard_stats(db: DbDep, _admin: DashboardAdmin):
    """仪表盘总览：核心计数 + 近 7 日趋势 + 订单状态占比 + 待处理事项。"""
    counts = {
        "members": db.execute(select(func.count()).select_from(User)).scalar() or 0,
        "products": db.execute(select(func.count()).select_from(Product).where(Product.is_deleted == 0)).scalar() or 0,
        "orders": db.execute(select(func.count()).select_from(Order)).scalar() or 0,
        "messages": db.execute(select(func.count()).select_from(Message)).scalar() or 0,
        "appointments": db.execute(select(func.count()).select_from(Appointment)).scalar() or 0,
        "news": db.execute(select(func.count()).select_from(News).where(News.is_deleted == 0)).scalar() or 0,
    }

    # 近 7 日订单数（按 created_date 分组；SQLite 下用 date() 函数截断到日）
    since = datetime.utcnow() - timedelta(days=6)
    order_rows = db.execute(
        select(func.date(Order.created_date), func.count())
        .where(Order.created_date >= since)
        .group_by(func.date(Order.created_date))
    ).all()
    visit_rows = db.execute(
        select(func.date(StatsVisit.created_date), func.count())
        .where(StatsVisit.created_date >= since)
        .group_by(func.date(StatsVisit.created_date))
    ).all()
    appt_rows = db.execute(
        select(func.date(Appointment.preferred_date), func.count())
        .where(Appointment.preferred_date >= since, Appointment.preferred_date.isnot(None))
        .group_by(func.date(Appointment.preferred_date))
    ).all()
    news_rows = db.execute(
        select(func.date(News.published_date), func.count())
        .where(News.published_date >= since, News.published_date.isnot(None), News.is_deleted == 0)
        .group_by(func.date(News.published_date))
    ).all()

    days = [(since + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    def fill(rows) -> list[int]:
        m = {str(k): v for k, v in rows}
        return [m.get(d, 0) for d in days]

    # 订单状态占比
    order_status_rows = db.execute(
        select(Order.status, func.count()).group_by(Order.status)
    ).all()
    order_status_dist = [{"status": k, "count": v} for k, v in order_status_rows]

    # 待处理事项
    todos = {
        # 草稿资讯（未发布）
        "draft_news": db.execute(
            select(func.count()).select_from(News).where(News.is_deleted == 0, News.is_published == False)
        ).scalar() or 0,
        # 待处理预约（pending）
        "pending_appointments": db.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "pending")
        ).scalar() or 0,
        # 待回复留言（pending）
        "pending_messages": db.execute(
            select(func.count()).select_from(Message).where(Message.status == "pending")
        ).scalar() or 0,
        # 最新会员（最近 5 个）
        "latest_members": [
            {"id": u.id, "nickname": u.nickname, "phone": u.phone, "created_date": str(u.created_date) if u.created_date else None}
            for u in db.execute(
                select(User).where(User.is_deleted == 0).order_by(User.id.desc()).limit(5)
            ).scalars().all()
        ],
    }

    return ApiResponse(
        data={
            "counts": counts,
            "days": days,
            "orders": fill(order_rows),
            "visits": fill(visit_rows),
            "appointments": fill(appt_rows),
            "news_trend": fill(news_rows),
            "order_status_dist": order_status_dist,
            "todos": todos,
        }
    )
