"""SQLAlchemy 模型层。

按数据库设计文档 §4 数据字典实现：
- 通用字段（AuditMixin）：is_activate + created_at(人) + created_date + updated_at(人) + updated_date
- 软删除字段（SoftDeleteMixin）：deleted_at + is_deleted
"""
from .admin_user import AdminUser
from .case import Case
from .category import Category
from .dept import Dept
from .product import Product
from .role import Role
from .user import User

__all__ = [
    "AdminUser",
    "Case",
    "Category",
    "Dept",
    "Product",
    "Role",
    "User",
]
