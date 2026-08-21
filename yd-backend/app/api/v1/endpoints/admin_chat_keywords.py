"""后台客服关键词管理 API（需 JWT + chat.* 权限）。"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import DbDep, require_permission
from app.models.admin_user import AdminUser
from app.schemas.chat_keyword import ChatKeywordIn, ChatKeywordOut
from app.schemas.common import ApiResponse, PageData
from app.services import chat_keyword_service

router = APIRouter(prefix="/admin/chat-keywords", tags=["后台-客服关键词"])


@router.get("", response_model=ApiResponse[PageData[ChatKeywordOut]])
def list_chat_keywords(
    db: DbDep,
    _admin: Annotated[AdminUser, Depends(require_permission("chat.view"))],
    keyword: str | None = Query(None),
    enabled: int | None = Query(None, description="0/1"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = chat_keyword_service.list_chat_keywords(
        db, keyword=keyword, enabled=enabled, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total else 0
    return ApiResponse(
        data=PageData[ChatKeywordOut](items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)
    )


@router.get("/{keyword_id}", response_model=ApiResponse[ChatKeywordOut])
def get_chat_keyword(
    keyword_id: int, db: DbDep, _admin: Annotated[AdminUser, Depends(require_permission("chat.view"))]
):
    c = chat_keyword_service.get_chat_keyword(db, keyword_id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关键词不存在")
    return ApiResponse(data=c)


@router.post("", response_model=ApiResponse[ChatKeywordOut])
def create_chat_keyword(
    payload: ChatKeywordIn, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("chat.edit"))]
):
    c = chat_keyword_service.create_chat_keyword(db, payload, admin.id)
    return ApiResponse(data=c, message=f"关键词《{c.keyword}》创建成功")


@router.put("/{keyword_id}", response_model=ApiResponse[ChatKeywordOut])
def update_chat_keyword(
    keyword_id: int,
    payload: ChatKeywordIn,
    db: DbDep,
    admin: Annotated[AdminUser, Depends(require_permission("chat.edit"))],
):
    c = chat_keyword_service.update_chat_keyword(db, keyword_id, payload, admin.id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关键词不存在")
    return ApiResponse(data=c, message=f"关键词《{c.keyword}》已更新")


@router.delete("/{keyword_id}", response_model=ApiResponse[dict])
def delete_chat_keyword(
    keyword_id: int, db: DbDep, admin: Annotated[AdminUser, Depends(require_permission("chat.edit"))]
):
    ok = chat_keyword_service.delete_chat_keyword(db, keyword_id, admin.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="关键词不存在")
    return ApiResponse(data={"id": keyword_id}, message=f"关键词 #{keyword_id} 已删除")
