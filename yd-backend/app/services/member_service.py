"""会员服务层：前台注册/登录/个人中心 + 后台列表/状态。"""
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.member import MemberListItem, MemberLoginIn, MemberOut, MemberRegisterIn


def register_member(payload: MemberRegisterIn, db: Session) -> MemberOut:
    """注册新会员（手机号唯一）。"""
    exists = db.scalar(select(User).where(User.phone == payload.phone, User.is_deleted == 0))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="手机号已注册")
    u = User(
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        email=payload.email,
        created_at=None,  # 会员无创建人概念
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return MemberOut.model_validate(u)


def login_member(payload: MemberLoginIn, db: Session) -> dict:
    """会员登录（校验密码 → 签发 JWT）。"""
    u = db.scalar(select(User).where(User.phone == payload.phone, User.is_deleted == 0))
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="手机号或密码错误")
    if u.is_activate != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    # 更新登录时间
    u.last_login_date = datetime.utcnow()
    db.commit()
    token = create_access_token(u.id, {"role": "member", "sub": str(u.id)})
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 7200,
        "member": MemberOut.model_validate(u).model_dump(),
    }


def get_member(db: Session, member_id: int) -> MemberOut | None:
    u = db.get(User, member_id)
    if not u or u.is_deleted:
        return None
    return MemberOut.model_validate(u)


def list_members_admin(
    db: Session,
    *,
    keyword: str | None = None,
    is_activate: int | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[MemberListItem], int]:
    q = select(User)
    if keyword:
        like = f"%{keyword}%"
        q = q.where((User.phone.like(like)) | (User.nickname.like(like)))
    if is_activate is not None:
        q = q.where(User.is_activate == is_activate)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    q = q.order_by(User.id.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(q).all()
    return [MemberListItem.model_validate(r) for r in rows], total


def update_member_status(db: Session, member_id: int, is_activate: bool) -> MemberListItem | None:
    u = db.get(User, member_id)
    if not u or u.is_deleted:
        return None
    u.is_activate = 1 if is_activate else 0
    db.commit()
    db.refresh(u)
    return MemberListItem.model_validate(u)


def delete_member(db: Session, member_id: int) -> bool:
    u = db.get(User, member_id)
    if not u or u.is_deleted:
        return False
    u.is_deleted = 1
    u.deleted_at = datetime.utcnow()
    db.commit()
    return True


__all__ = [
    "register_member", "login_member", "get_member",
    "list_members_admin", "update_member_status", "delete_member",
]