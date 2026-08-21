"""后台部门管理 API（需 JWT）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.common import ApiResponse
from app.schemas.dept import DeptCreate, DeptNode
from app.services import dept_service

router = APIRouter(prefix="/admin/depts", tags=["后台-部门"])


@router.get("", response_model=ApiResponse[list[dict]])
def list_depts(db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("dept.view"))]):
    """后台：部门列表（树形）。"""
    nodes = dept_service.list_depts(db)
    tree = dept_service.build_tree(nodes)
    return ApiResponse(data=tree)


@router.get("/flat", response_model=ApiResponse[list[DeptNode]])
def list_depts_flat(db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("dept.view"))]):
    """后台：部门扁平列表（用于下拉选择 parent_id）。"""
    nodes = dept_service.list_depts(db)
    return ApiResponse(data=nodes)


@router.post("", response_model=ApiResponse[DeptNode])
def create_dept(payload: DeptCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("dept.edit"))]):
    d = dept_service.create_dept(db, payload, admin.id)
    return ApiResponse(data=d, message=f"部门《{d.name}》已创建")


@router.put("/{dept_id}", response_model=ApiResponse[DeptNode])
def update_dept(dept_id: int, payload: DeptCreate, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("dept.edit"))]):
    d = dept_service.update_dept(db, dept_id, payload, admin.id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="部门不存在")
    return ApiResponse(data=d, message=f"部门《{d.name}》已更新")


@router.delete("/{dept_id}", response_model=ApiResponse[dict])
def delete_dept(dept_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("dept.edit"))]):
    ok = dept_service.delete_dept(db, dept_id, _admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败：部门有子部门或被引用")
    return ApiResponse(data={"id": dept_id}, message=f"部门 #{dept_id} 已删除")