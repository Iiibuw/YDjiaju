"""前台分类 API（公开）：series/space/category 启用中分类，供产品中心筛选。"""
from fastapi import APIRouter, Query

from app.core.deps import DbDep
from app.schemas.category import CategoryOut
from app.schemas.common import ApiResponse
from app.services import category_service

router = APIRouter(prefix="/public/categories", tags=["前台-分类"])


@router.get("", response_model=ApiResponse[list[CategoryOut]])
def list_categories(
    db: DbDep,
    kind: str | None = Query(None, description="series/space/category，缺省返回全部启用分类"),
):
    """启用中的分类（扁平，按 kind+sort）。"""
    return ApiResponse(data=category_service.options(db, kind=kind))
