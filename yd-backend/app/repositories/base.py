"""仓储层 + 数据范围过滤（ADR-004）。

仅对 `DATA_SCOPED_MODELS` 白名单内的表做范围过滤；其余表（内容域等）走全局可见。
"""
import enum

from sqlalchemy import literal
from sqlalchemy.orm import Query
from sqlalchemy.sql import and_, or_

from app.db.session import SessionLocal
from app.models.admin_user import AdminUser


class DataScope(str, enum.Enum):
    ALL = "ALL"        # 全部
    REGION = "REGION"  # 本区域
    STORE = "STORE"    # 本门店
    SELF = "SELF"      # 仅自己创建


# 仅这些表的数据受 data_scope 约束（与数据库文档 §2.1.5 数据隔离章节一致）
DATA_SCOPED_MODELS: set[str] = {
    "orders",
    "appointments",
    "messages",
    "job_applications",
}


def is_data_scoped(model) -> bool:
    """判断模型表是否需要数据范围过滤。"""
    return getattr(model, "__tablename__", None) in DATA_SCOPED_MODELS


def get_admin_data_scope(admin: AdminUser) -> DataScope:
    """把 AdminUser.data_scope 字符串解析为枚举。"""
    try:
        return DataScope(admin.data_scope)
    except ValueError:
        return DataScope.SELF


def apply_data_scope(query: Query, model, admin: AdminUser) -> Query:
    """根据管理员数据范围自动注入 WHERE 条件（ADR-004）。

    非白名单表返回原 query（视为全局可见）。
    委托给本模块 ensure_data_scope 不重复。
    """
    return ensure_data_scope(query, model, admin)


def ensure_data_scope(query: Query, model, admin: AdminUser) -> Query:
    """详见 apply_data_scope 文档。"""
    if not is_data_scoped(model):
        return query

    scope = get_admin_data_scope(admin)

    if scope == DataScope.ALL:
        return query

    if scope == DataScope.SELF:
        return query.filter(getattr(model, "created_at", None) == admin.id)

    # REGION / STORE：暂以 created_at=admin.id 作保守实现，M1 阶段简化
    # M2 阶段会接入 admin_regions 关联，扩展为 region_code/store_code 过滤
    if hasattr(model, "region_code"):
        return query.filter(getattr(model, "region_code").is_(None))  # 保守：只看不带区域的
    return query.filter(literal(False))  # 兜底：拒绝访问（防止越权）
