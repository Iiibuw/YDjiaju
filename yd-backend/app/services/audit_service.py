"""审计服务层：写审计日志（helper）+ 分页查询。

写操作统一调用 ``write_audit_log``，payload 必须脱敏（不落密码/token/手机号）。
"""
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def write_audit_log(
    db: Session,
    *,
    admin_id: int | None,
    action: str,
    resource: str,
    resource_id: int | None = None,
    payload: dict[str, Any] | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """写入一条操作审计（payload 应为已脱敏的摘要信息）。"""
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        payload=payload,
        ip=ip,
        user_agent=user_agent,
    )
    db.add(log)
    db.flush()
    return log


def list_audit_logs(
    db: Session,
    *,
    admin_id: int | None = None,
    action: str | None = None,
    resource: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[AuditLog], int]:
    q = select(AuditLog)
    if admin_id is not None:
        q = q.where(AuditLog.admin_id == admin_id)
    if action:
        q = q.where(AuditLog.action == action)
    if resource:
        q = q.where(AuditLog.resource == resource)
    total = db.execute(select(func.count()).select_from(q.subquery())).scalar() or 0
    q = q.order_by(AuditLog.created_date.desc(), AuditLog.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    return list(db.execute(q).scalars().all()), total


__all__ = ["write_audit_log", "list_audit_logs"]
