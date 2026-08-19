"""Lite 模式数据库初始化 + 种子数据。

用法（venv 激活后）：
    cd yd-backend
    cp .env.lite .env    # 切到 SQLite 模式
    uv run python scripts/init_lite.py

会：
1. 删除旧 yd_lite.db
2. 通过 Base.metadata.create_all 重建 7 张 M1 表
3. 插入种子数据：admin/超管 + 1 系列 + 4 类目 + 2 产品
"""
import sys
from pathlib import Path

# 把项目根加入路径
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ====== 清空 pydantic-settings 缓存（让 .env 重新生效） ======
from app.core.config import get_settings
from app.core.security import hash_password

get_settings.cache_clear()
from app.core import config as _cfg

# 确保是 lite 模式
_cfg.settings.DB_TYPE = "sqlite"
_cfg.settings.DB_PATH = str(ROOT / "yd_lite.db")

# 重新构建 engine
from app.db import session as _session
from app.db.base import Base
from sqlalchemy import create_engine

_session.engine.dispose()
_session.engine = create_engine(
    _cfg.settings.database_url,
    connect_args={"check_same_thread": False},
    echo=_cfg.settings.DEBUG,
    future=True,
)
_session.SessionLocal.configure(bind=_session.engine)

# ====== 删除旧数据库 ======
DB_FILE = ROOT / "yd_lite.db"

# ====== 重建表 ======
if DB_FILE.exists():
    print(f"📍 SQLite 文件已存在：{DB_FILE.name}（将清空表）")
else:
    print(f"📍 新建 SQLite 文件：{DB_FILE.name}")
print(f"📍 URL = {_cfg.settings.database_url}")

print("\n🏗️  重建表结构...")

# 先 import 所有模型确保 metadata 注册
from app.models import (  # noqa: F401
    AdminUser, Role, Dept, User, Category, Product, Case,
)

# 删表 + 建表
Base.metadata.drop_all(bind=_session.engine)
Base.metadata.create_all(bind=_session.engine)
print(f"  ✓ 创建 {len(Base.metadata.tables)} 张表：")
for t in sorted(Base.metadata.tables.keys()):
    print(f"    - {t}")

# ====== 种子数据 ======
print("\n🌱 灌入种子数据...")

from app.models.admin_user import AdminUser
from app.models.category import Category
from app.models.dept import Dept
from app.models.product import Product
from app.models.role import Role

with _session.SessionLocal() as db:
    # ----- 部门 -----
    tech_dept = Dept(name="研发中心", code="RD", parent_id=None, sort=1, is_activate=1)
    db.add(tech_dept)
    db.flush()
    print(f"  ✓ 部门: {tech_dept.name} (id={tech_dept.id})")

    # ----- 角色 -----
    admin_role = Role(
        name="超级管理员",
        code="admin",
        data_scope="ALL",
        description="内置超管",
        sort=1,
        is_activate=1,
    )
    db.add(admin_role)
    db.flush()
    print(f"  ✓ 角色: {admin_role.name} (id={admin_role.id})")

    # ----- 管理员 -----
    admin = AdminUser(
        username="admin",
        password_hash=hash_password("admin123"),
        real_name="超级管理员",
        email="admin@yd.com",
        dept_id=tech_dept.id,
        role_id=admin_role.id,
        data_scope="ALL",
        is_activate=1,
    )
    db.add(admin)
    db.flush()
    print(f"  ✓ 超管: {admin.username} (id={admin.id})")

    # ----- 类目 -----
    space_dining = Category(name="餐厅", kind="space", parent_id=None, sort=1, enabled=1)
    space_bedroom = Category(name="卧室", kind="space", parent_id=None, sort=2, enabled=1)
    series_walnut = Category(name="胡桃禮系列", kind="series", parent_id=None, sort=1, enabled=1)
    cat_table = Category(name="餐桌", kind="category", parent_id=space_dining.id, sort=1, enabled=1)

    db.add_all([space_dining, space_bedroom, series_walnut, cat_table])
    db.flush()
    print(f"  ✓ 类目: 4 个（{space_dining.name}, {space_bedroom.name}, {series_walnut.name}, {cat_table.name}）")

    # ----- 产品 -----
    p1 = Product(
        product_code="YD-001-180",
        name="胡桃禮·实木餐桌",
        subtitle="现代简约 · 餐厅精选",
        cover_url="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800",
        min_price_cents=128000,
        max_price_cents=168000,
        is_top=1,
        status="on_sale",
        category_id=cat_table.id,
        series_id=series_walnut.id,
        space_id=space_dining.id,
        description="<p>选用北美黑胡桃木，纹理自然、质地坚硬。</p>",
        extra_specs={"材质": "黑胡桃木", "尺寸": "1800×900×750mm"},
        sort=1,
    )
    p2 = Product(
        product_code="YD-002-150",
        name="胡桃禮·实木餐边柜",
        subtitle="收纳美学 · 餐厅必备",
        cover_url="https://images.unsplash.com/photo-1567538096342-cd31b4c75e9b?w=800",
        min_price_cents=98000,
        max_price_cents=98000,
        is_top=1,
        status="on_sale",
        category_id=cat_table.id,
        series_id=series_walnut.id,
        space_id=space_dining.id,
        sort=2,
    )
    db.add_all([p1, p2])
    db.flush()
    print(f"  ✓ 产品: 2 个（{p1.name}, {p2.name}）")

    db.commit()

print("\n✅ Lite 数据库初始化完成！")
print(f"   路径: {DB_FILE}")
print(f"   登录: admin / admin123")
