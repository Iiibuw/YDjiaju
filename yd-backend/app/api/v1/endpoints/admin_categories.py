"""后台分类管理 API（需 JWT + category.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.category import CategoryIn, CategoryOut
from app.schemas.common import ApiResponse
from app.services import category_service

router = APIRouter(prefix="/admin/categories", tags=["后台-分类"])


@router.get("", response_model=ApiResponse[list[CategoryOut]])
def list_categories(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("category.view"))],
    keyword: str | None = Query(None),
    kind: str | None = Query(None, description="series/space/category"),
):
    """分类列表（树形）。"""
    items = category_service.list_categories(db, keyword=keyword, kind=kind)
    return ApiResponse(data=category_service.build_tree(items))


@router.get("/options", response_model=ApiResponse[list[CategoryOut]])
def category_options(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("category.view"))],
    kind: str | None = Query(None, description="series/space/category"),
):
    """分类下拉（扁平，启用中）。"""
    return ApiResponse(data=category_service.options(db, kind=kind))


@router.post("", response_model=ApiResponse[CategoryOut])
def create_category(
    payload: CategoryIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("category.create"))]
):
    c = category_service.create_category(db, payload, admin.id)
    return ApiResponse(data=c, message=f"分类《{c.name}》创建成功")


@router.put("/{category_id}", response_model=ApiResponse[CategoryOut])
def update_category(
    category_id: int,
    payload: CategoryIn,
    db: DbDep,
    admin: Annotated[AdminUser, Depends(require_permission("category.edit"))],
):
    c = category_service.update_category(db, category_id, payload, admin.id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在或父级指向自身")
    return ApiResponse(data=c, message=f"分类《{c.name}》已更新")


@router.delete("/{category_id}", response_model=ApiResponse[dict])
def delete_category(
    category_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("category.delete"))]
):
    ok = category_service.delete_category(db, category_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="删除失败：分类不存在或有子分类")
    return ApiResponse(data={"id": category_id}, message=f"分类 #{category_id} 已删除")
