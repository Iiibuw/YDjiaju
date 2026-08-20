"""认证相关 Pydantic 模型。"""
from pydantic import BaseModel, Field


class CaptchaOut(BaseModel):
    """GET /api/v1/auth/captcha 响应（前端用 captcha_id 关联）。"""

    captcha_id: str = Field(description="图形验证码 ID，前端提交时同答案一起返回")
    captcha_image: str = Field(description="base64 编码的 PNG 图片，data URI")
    expires_in: int = Field(description="过期时间（秒）")


class LoginIn(BaseModel):
    """POST /api/v1/auth/login 请求体。

    字段名严格对齐前端 form（技术文档 §4.1）。
    """

    username: str = Field(min_length=3, max_length=64, description="登录名/手机号")
    password: str = Field(min_length=6, max_length=128, description="密码")
    captcha_id: str = Field(min_length=8, max_length=64, description="图形验证码 ID")
    captcha_code: str = Field(min_length=4, max_length=8, description="图形验证码文本")


class TokenOut(BaseModel):
    """POST /api/v1/auth/login 响应。"""

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(description="过期时间（秒）")
    admin_id: int = Field(description="管理员 ID")
    real_name: str | None = Field(default=None)
    role: str | None = Field(default=None, description="主角色代码")
    avatar_url: str | None = Field(default=None)


class AdminProfileOut(BaseModel):
    """GET /api/v1/auth/me 响应。"""

    id: int
    username: str
    real_name: str | None
    nickname: str | None
    avatar_url: str | None
    email: str | None = Field(default=None, description="邮箱")
    role: str | None = Field(description="主角色代码（来自 admin_users.role_id → roles.code）")
    dept_name: str | None = Field(default=None, description="部门名")
    data_scope: str = Field(description="ALL/REGION/STORE/SELF")


class ChangePasswordIn(BaseModel):
    """POST /api/v1/auth/change-password 请求体——改自己密码。"""

    old_password: str = Field(min_length=6, max_length=128, description="当前密码")
    new_password: str = Field(min_length=6, max_length=128, description="新密码（至少 6 位）")
