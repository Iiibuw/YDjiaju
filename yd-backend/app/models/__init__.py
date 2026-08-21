"""SQLAlchemy 模型层。

按数据库设计文档 §4 数据字典实现（共 34 张表）：
- 通用字段（AuditMixin）：is_activate + created_at(人) + created_date + updated_at(人) + updated_date
- 软删除字段（SoftDeleteMixin）：deleted_at + is_deleted
- 业务表各自声明字段、外键、索引、CHECK 约束
"""
from .about_image import AboutImage
from .about_section import AboutSection
from .admin_role import AdminRole
from .admin_region import AdminRegion
from .admin_user import AdminUser
from .appointment import Appointment
from .audit_log import AuditLog
from .banner import Banner
from .case import Case
from .case_image import CaseImage
from .category import Category
from .cart_item import CartItem
from .chat_keyword import ChatKeyword
from .dept import Dept
from .download import Download
from .job import Job
from .job_application import JobApplication
from .message import Message
from .news import News
from .order import Order
from .order_item import OrderItem
from .payment import Payment
from .permission import Permission
from .product import Product
from .product_image import ProductImage
from .product_sku import ProductSku
from .role import Role
from .role_permission import RolePermission
from .site_config import SiteConfig
from .stats_visit import StatsVisit
from .user import User
from .user_address import UserAddress
from .user_favorite import UserFavorite
from .user_search_log import UserSearchLog

__all__ = [
    "AboutImage",
    "AboutSection",
    "AdminRole",
    "AdminRegion",
    "AdminUser",
    "Appointment",
    "AuditLog",
    "Banner",
    "Case",
    "CaseImage",
    "Category",
    "CartItem",
    "ChatKeyword",
    "Dept",
    "Download",
    "Job",
    "JobApplication",
    "Message",
    "News",
    "Order",
    "OrderItem",
    "Payment",
    "Permission",
    "Product",
    "ProductImage",
    "ProductSku",
    "Role",
    "RolePermission",
    "SiteConfig",
    "StatsVisit",
    "User",
    "UserAddress",
    "UserFavorite",
    "UserSearchLog",
]
