"""后台会员 + 留言管理 API（需 JWT）。"""
from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import CurrentAdmin, DbDep
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.member import MemberListItem
from app.schemas.message import MessageOut, MessageReplyIn
from app.services import member_service, message_service

router = APIRouter(prefix="/admin", tags=["后台-会员与留言"])


# ===== 会员 =====

@router.get("/members", response_model=ApiResponse[dict])
def list_members(
    db: DbDep,
    _admin: CurrentAdmin,
    keyword: str | None = None,
    is_activate: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """后台：会员列表。"""
    items, total = member_service.list_members_admin(
        db, keyword=keyword,
        is_activate=(1 if is_activate else 0) if is_activate is not None else None,
        page=page, page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": [MemberListItem.model_validate(i) for i in items],
        "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })


@router.put("/members/{member_id}/status", response_model=ApiResponse[MemberListItem])
def update_member_status(member_id: int, payload: dict, db: DbDep, _admin: CurrentAdmin):
    """后台：启用/禁用会员。body: {"is_activate": bool}"""
    is_activate = bool(payload.get("is_activate"))
    m = member_service.update_member_status(db, member_id, is_activate)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会员不存在")
    return ApiResponse(data=m, message="已启用" if is_activate else "已禁用")


@router.delete("/members/{member_id}", response_model=ApiResponse[dict])
def delete_member(member_id: int, db: DbDep, _admin: CurrentAdmin):
    ok = member_service.delete_member(db, member_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会员不存在")
    return ApiResponse(data={"id": member_id}, message=f"会员 #{member_id} 已删除")


# ===== 留言 =====

@router.get("/messages", response_model=ApiResponse[dict])
def list_messages(
    db: DbDep,
    _admin: CurrentAdmin,
    status_filter: str | None = Query(None, alias="status", description="pending/replied/archived"),
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """后台：留言列表。"""
    items, total = message_service.list_messages_admin(
        db, status_filter=status_filter, keyword=keyword, page=page, page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size if page_size else 0
    return ApiResponse(data={
        "items": [MessageOut.model_validate(i) for i in items],
        "total": total, "page": page, "page_size": page_size, "total_pages": total_pages,
        "meta": PaginationMeta(total=total, page=page, page_size=page_size, total_pages=total_pages).model_dump(),
    })


@router.post("/messages/{message_id}/reply", response_model=ApiResponse[MessageOut])
def reply_message(message_id: int, payload: MessageReplyIn, db: DbDep, _admin: CurrentAdmin):
    m = message_service.reply_message(db, message_id, payload)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="留言不存在")
    return ApiResponse(data=m, message="回复成功")


@router.delete("/messages/{message_id}", response_model=ApiResponse[dict])
def delete_message(message_id: int, db: DbDep, _admin: CurrentAdmin):
    ok = message_service.delete_message(db, message_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="留言不存在")
    return ApiResponse(data={"id": message_id}, message=f"留言 #{message_id} 已删除")