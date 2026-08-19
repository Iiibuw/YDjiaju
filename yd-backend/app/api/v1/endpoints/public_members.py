"""前台会员 + 留言 API（公开）。"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import DbDep, get_current_member
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.member import MemberLoginIn, MemberOut, MemberRegisterIn
from app.schemas.message import MessageCreate, MessageOut
from app.services import member_service, message_service

router = APIRouter(prefix="/members", tags=["前台-会员"])


@router.post("/register", response_model=ApiResponse[MemberOut])
def register(payload: MemberRegisterIn, db: DbDep):
    m = member_service.register_member(payload, db)
    return ApiResponse(data=m, message=f"注册成功，欢迎 {m.nickname or m.phone}")


@router.post("/login", response_model=ApiResponse[dict])
def login(payload: MemberLoginIn, db: DbDep):
    """会员登录（M2-2-B 简化：直接密码登录，不做验证码校验，生产走 SMS 验证码）。"""
    data = member_service.login_member(payload, db)
    return ApiResponse(data=data, message="登录成功")


@router.get("/me", response_model=ApiResponse[MemberOut])
def me(db: DbDep, current: User = Depends(get_current_member)):
    return ApiResponse(data=MemberOut.model_validate(current))


@router.post("/messages", response_model=ApiResponse[MessageOut])
def create_message(payload: MessageCreate, db: DbDep):
    m = message_service.create_message(payload, db)
    return ApiResponse(data=m, message="留言已提交，我们会尽快回复您")