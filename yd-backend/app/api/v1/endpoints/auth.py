"""GET /api/v1/auth/captcha + POST /api/v1/auth/login + GET /api/v1/auth/me。"""
from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.deps import CurrentAdmin, DbDep
from app.schemas.auth import AdminProfileOut, CaptchaOut, ChangePasswordIn, LoginIn, TokenOut
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter()


@router.get("/auth/captcha", response_model=ApiResponse[CaptchaOut])
def get_captcha():
    """获取图形验证码。"""
    return ApiResponse(data=auth_service.new_captcha())


@router.get("/auth/captcha-image/{captcha_id}")
def get_captcha_image(captcha_id: str):
    """验证码 PNG 字节直连（供 <img> 标签加载）。"""
    png = auth_service.get_captcha_image(captcha_id)
    if png is None:
        raise HTTPException(status_code=404, detail="验证码不存在或已过期")
    return Response(content=png, media_type="image/png")


@router.post("/auth/login", response_model=ApiResponse[TokenOut])
def login(payload: LoginIn, db: DbDep):
    """登录。错误锁定 15 分钟 / 5 次。"""
    return ApiResponse(data=auth_service.login(payload, db))


@router.get("/auth/me", response_model=ApiResponse[AdminProfileOut])
def me(admin: CurrentAdmin, db: DbDep):
    """当前管理员资料（解析 Bearer token）。"""
    return ApiResponse(data=AdminProfileOut(**auth_service.get_admin_profile(admin, db)))


@router.post("/auth/logout")
def logout():
    """登出。M1 占位（M2 用 Redis 黑名单实现）。"""
    return ApiResponse(message="已登出（前端删除本地 token）")


@router.post("/auth/change-password", response_model=ApiResponse[None])
def change_password(payload: ChangePasswordIn, admin: CurrentAdmin, db: DbDep):
    """改自己密码——校验旧密码后用 bcrypt 写入新密码。"""
    auth_service.change_password(admin.id, payload.old_password, payload.new_password, db)
    return ApiResponse(message="密码修改成功")
