"""GET /api/v1/auth/captcha + POST /api/v1/auth/login + GET /api/v1/auth/me。"""
from fastapi import APIRouter, Depends

from app.core.deps import CurrentAdmin, DbDep
from app.schemas.auth import AdminProfileOut, CaptchaOut, LoginIn, TokenOut
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter()


@router.get("/auth/captcha", response_model=ApiResponse[CaptchaOut])
def get_captcha():
    """获取图形验证码。"""
    return ApiResponse(data=auth_service.new_captcha())


@router.post("/auth/login", response_model=ApiResponse[TokenOut])
def login(payload: LoginIn, db: DbDep):
    """登录。错误锁定 15 分钟 / 5 次。"""
    return ApiResponse(data=auth_service.login(payload, db))


@router.get("/auth/me", response_model=ApiResponse[AdminProfileOut])
def me(admin: CurrentAdmin):
    """当前管理员资料（解析 Bearer token）。"""
    return ApiResponse(data=AdminProfileOut(**auth_service.get_admin_profile(admin)))


@router.post("/auth/logout")
def logout():
    """登出。M1 占位（M2 用 Redis 黑名单实现）。"""
    return ApiResponse(message="已登出（前端删除本地 token）")
