"""后台审计日志查询 API（需 JWT + system.audit 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PageData
from app.services import audit_service

router = APIRouter(prefix="/admin/audit-logs", tags=["后台-审计"])

AuditAdmin = Annotated[AdminUser, Depends(require_permission("system.audit"))]


@router.get("", response_model=ApiResponse[PageData[dict]])
def list_audit_logs(
    db: DbDep,
    _admin: AuditAdmin,
    admin_id: int | None = Query(None, description="操作人"),
    action: str | None = Query(None, description="操作类型，如 product.create"),
    resource: str | None = Query(None, description="资源类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = audit_service.list_audit_logs(
        db, admin_id=admin_id, action=action, resource=resource, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    data = [
        {
            "id": a.id,
            "admin_id": a.admin_id,
            "action": a.action,
            "resource": a.resource,
            "resource_id": a.resource_id,
            "payload": a.payload,
            "ip": a.ip,
            "created_date": a.created_date.isoformat() if a.created_date else None,
        }
        for a in items
    ]
    return ApiResponse(data=PageData[dict](items=data, total=total, page=page, page_size=page_size, total_pages=total_pages))
