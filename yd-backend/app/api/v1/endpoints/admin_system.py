"""后台系统管理 API（角色 / 权限 / 管理员，需 JWT + system.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse, PageData
from app.schemas.system import (
    AdminUserIn,
    AdminUserOut,
    AdminUserUpdate,
    PasswordIn,
    PermissionOut,
    RoleIn,
    RoleOut,
    RolePermIn,
)
from app.services import audit_service, system_service

router = APIRouter(prefix="/admin", tags=["后台-系统管理"])

ADMIN = Annotated[AdminUser, Depends(require_permission("system.role"))]
ADMIN_PERM = Annotated[AdminUser, Depends(require_permission("system.permission"))]


# ===== 角色 =====

@router.get("/roles", response_model=ApiResponse[PageData[RoleOut]])
def list_roles(
    db: DbDep,
    _admin: ADMIN,
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    items, total = system_service.list_roles(db, keyword=keyword, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(data=PageData[RoleOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages))


@router.post("/roles", response_model=ApiResponse[RoleOut])
def create_role(payload: RoleIn, db: DbDep, admin: ADMIN):
    r = system_service.create_role(db, payload, admin.id)
    audit_service.write_audit_log(db, admin_id=admin.id, action="role.create", resource="role", resource_id=r.id)
    db.commit()
    return ApiResponse(data=r, message=f"角色《{r.name}》创建成功")


@router.put("/roles/{role_id}", response_model=ApiResponse[RoleOut])
def update_role(role_id: int, payload: RoleIn, db: DbDep, admin: ADMIN):
    r = system_service.update_role(db, role_id, payload, admin.id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在或内置角色禁止修改 code")
    audit_service.write_audit_log(db, admin_id=admin.id, action="role.update", resource="role", resource_id=role_id)
    db.commit()
    return ApiResponse(data=r, message=f"角色《{r.name}》已更新")


@router.delete("/roles/{role_id}", response_model=ApiResponse[dict])
def delete_role(role_id: int, db: DbDep, admin: ADMIN):
    ok = system_service.delete_role(db, role_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败：内置角色/角色不存在/仍有管理员使用")
    audit_service.write_audit_log(db, admin_id=admin.id, action="role.delete", resource="role", resource_id=role_id)
    db.commit()
    return ApiResponse(data={"id": role_id}, message=f"角色 #{role_id} 已删除")


@router.put("/roles/{role_id}/permissions", response_model=ApiResponse[RoleOut])
def set_role_permissions(role_id: int, payload: RolePermIn, db: DbDep, admin: ADMIN):
    r = system_service.set_role_permissions(db, role_id, payload.permission_ids, admin.id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    audit_service.write_audit_log(
        db, admin_id=admin.id, action="role.grant", resource="role", resource_id=role_id,
        payload={"permission_count": len(payload.permission_ids)},
    )
    db.commit()
    return ApiResponse(data=r, message=f"角色《{r.name}》已授权 {len(payload.permission_ids)} 个权限点")


# ===== 权限 =====

@router.get("/permissions", response_model=ApiResponse[dict])
def list_permissions(
    db: DbDep,
    _admin: ADMIN_PERM,
    module: str | None = Query(None, description="按模块筛选"),
):
    """权限点列表（按模块分组）。"""
    perms = system_service.list_permissions(db, module=module)
    return ApiResponse(data=system_service.permission_modules(perms))


@router.get("/permissions/flat", response_model=ApiResponse[list[PermissionOut]])
def list_permissions_flat(
    db: DbDep,
    _admin: ADMIN_PERM,
    module: str | None = Query(None),
):
    """权限点扁平列表。"""
    return ApiResponse(data=[PermissionOut.model_validate(p) for p in system_service.list_permissions(db, module=module)])


# ===== 管理员 =====

@router.get("/users", response_model=ApiResponse[PageData[AdminUserOut]])
def list_admin_users(
    db: DbDep,
    _admin: ADMIN,
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = system_service.list_admin_users(db, keyword=keyword, page=page, page_size=page_size)
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[AdminUserOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
    )


@router.post("/users", response_model=ApiResponse[AdminUserOut])
def create_admin_user(payload: AdminUserIn, db: DbDep, admin: ADMIN):
    u = system_service.create_admin_user(db, payload, admin.id)
    audit_service.write_audit_log(db, admin_id=admin.id, action="admin.create", resource="admin", resource_id=u.id)
    db.commit()
    return ApiResponse(data=u, message=f"管理员 {u.username} 创建成功")


@router.put("/users/{user_id}", response_model=ApiResponse[AdminUserOut])
def update_admin_user(user_id: int, payload: AdminUserUpdate, db: DbDep, admin: ADMIN):
    u = system_service.update_admin_user(db, user_id, payload, admin.id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员不存在或为内置超管")
    audit_service.write_audit_log(db, admin_id=admin.id, action="admin.update", resource="admin", resource_id=user_id)
    db.commit()
    return ApiResponse(data=u, message=f"管理员 #{user_id} 已更新")


@router.put("/users/{user_id}/password", response_model=ApiResponse[dict])
def reset_password(user_id: int, payload: PasswordIn, db: DbDep, admin: ADMIN):
    ok = system_service.reset_password(db, user_id, payload.password, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员不存在")
    audit_service.write_audit_log(db, admin_id=admin.id, action="admin.password", resource="admin", resource_id=user_id)
    db.commit()
    return ApiResponse(data={"id": user_id}, message="密码已重置")


@router.delete("/users/{user_id}", response_model=ApiResponse[dict])
def delete_admin_user(user_id: int, db: DbDep, admin: ADMIN):
    ok = system_service.delete_admin_user(db, user_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败：管理员不存在/内置超管/不能删除自己")
    audit_service.write_audit_log(db, admin_id=admin.id, action="admin.delete", resource="admin", resource_id=user_id)
    db.commit()
    return ApiResponse(data={"id": user_id}, message=f"管理员 #{user_id} 已删除")
