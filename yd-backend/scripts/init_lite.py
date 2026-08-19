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

    # ----- 资讯（5 条，2 个分类） -----
    from datetime import datetime, timedelta
    from app.models.news import News

    now = datetime.utcnow()
    news_list = [
        News(
            title="YD 家居荣获 2026 中国家具创新品牌奖",
            subtitle="品牌动态",
            cover_url="https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800",
            summary="8 月 15 日，YD 家居凭借胡桃禮系列在 2026 中国家具创新品牌评选中脱颖而出...",
            content="<p>8 月 15 日，YD 家居凭借胡桃禮系列在 2026 中国家具创新品牌评选中脱颖而出，荣获年度创新品牌奖。</p><p>本次评选由...</p>",
            author="YD 编辑部",
            category="company",
            view_count=1280,
            is_published=1,
            is_top=1,
            is_recommend=1,
            sort=100,
            published_date=now - timedelta(days=1),
            created_at=1, updated_at=1,
        ),
        News(
            title="关于我司参加 2026 广州国际家具博览会的通知",
            subtitle="展会信息",
            cover_url="https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
            summary="我司将于 9 月 10 日至 13 日参加广州国际家具博览会...展位号：5B12",
            content="<p>我司将于 9 月 10 日至 13 日参加广州国际家具博览会，欢迎新老客户莅临指导。</p><p><strong>展位号：5B12</strong></p>",
            author="市场部",
            category="company",
            view_count=856,
            is_published=1,
            is_top=0,
            is_recommend=1,
            sort=90,
            published_date=now - timedelta(days=3),
            created_at=1, updated_at=1,
        ),
        News(
            title="2026 年家居行业消费趋势报告",
            subtitle="行业洞察",
            cover_url="https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800",
            summary="报告显示，2026 年中国家装行业整体规模超 5 万亿元，新中式风格持续走热...",
            content="<p>报告显示，2026 年中国家装行业整体规模超 5 万亿元，新中式风格持续走热...</p>",
            author="行业研究部",
            category="industry",
            view_count=2340,
            is_published=1,
            is_top=1,
            is_recommend=0,
            sort=80,
            published_date=now - timedelta(days=5),
            created_at=1, updated_at=1,
        ),
        News(
            title="环保新规：水性漆将全面替代油性漆",
            subtitle="政策法规",
            cover_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
            summary="工信部新规要求 2026 年 12 月起，家居行业全面使用水性漆...",
            content="<p>工信部新规要求 2026 年 12 月起，家居行业全面使用水性漆。</p>",
            author="政策法规组",
            category="industry",
            view_count=1567,
            is_published=1,
            is_top=0,
            is_recommend=1,
            sort=70,
            published_date=now - timedelta(days=7),
            created_at=1, updated_at=1,
        ),
        News(
            title="胡桃禮系列新品发布会将于 10 月举行",
            subtitle="草稿预览",
            cover_url="https://images.unsplash.com/photo-1581539250439-c96689b5164a?w=800",
            summary="胡桃禮系列全新升级产品将于 10 月 1 日正式发布...",
            content="<p>胡桃禮系列全新升级产品将于 10 月 1 日正式发布，敬请期待。</p>",
            author="品牌部",
            category="company",
            view_count=0,
            is_published=0,  # 草稿状态
            is_top=0,
            is_recommend=0,
            sort=0,
            published_date=None,
            created_at=1, updated_at=1,
        ),
    ]
    db.add_all(news_list)
    db.flush()
    print(f"  ✓ 资讯: 5 条（4 已发布 + 1 草稿）")

    # ----- 招聘岗位（3 个） -----
    from app.models.job import Job

    jobs = [
        Job(
            title="高级家具设计师",
            category="social",
            department="设计中心",
            location="佛山",
            salary_min_cents=1500000,  # 1.5w
            salary_max_cents=2500000,  # 2.5w
            headcount=2,
            description="<p>负责实木家具的产品设计与研发。</p>",
            requirement="<ul><li>5 年以上实木家具设计经验</li><li>熟练使用 SolidWorks/Rhino</li></ul>",
            publish_date=now - timedelta(days=2),
            expire_date=now + timedelta(days=60),
            created_at=1, updated_at=1,
        ),
        Job(
            title="电商运营专员",
            category="social",
            department="电商部",
            location="佛山",
            salary_min_cents=800000,
            salary_max_cents=1200000,
            headcount=1,
            description="<p>负责天猫/京东旗舰店的日常运营。</p>",
            requirement="<ul><li>3 年以上家居电商运营经验</li></ul>",
            publish_date=now - timedelta(days=5),
            expire_date=now + timedelta(days=30),
            created_at=1, updated_at=1,
        ),
        Job(
            title="2027 届校园招聘 - 产品设计培训生",
            category="campus",
            department="管培生项目",
            location="佛山",
            salary_min_cents=800000,
            salary_max_cents=1200000,
            headcount=10,
            description="<p>2 年轮岗 + 双导师制。</p>",
            requirement="<ul><li>2027 届本科及以上应届生</li><li>专业不限，家具/工业设计优先</li></ul>",
            publish_date=now - timedelta(days=10),
            expire_date=now + timedelta(days=90),
            created_at=1, updated_at=1,
        ),
    ]
    db.add_all(jobs)
    db.flush()
    print(f"  ✓ 招聘岗位: 3 个（2 社招 + 1 校招）")

    # ----- 案例（3 个） -----
    from app.models.case import Case as CaseModel

    cases = [
        CaseModel(
            title="胡桃禮·广州海珠湾花园别墅",
            category_id=space_dining.id,
            cover_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800",
            style="现代简约",
            area="280㎡",
            description="<p>客户为三代同堂的 6 口之家，整体调性强调温馨与品质感。</p><p>餐厅以胡桃禮实木餐桌为核心，搭配北美黑胡桃餐边柜，营造现代简约却温暖的就餐氛围。</p><h3>设计要点</h3><ul><li>客厅：胡桃木电视柜 + 真皮主沙发</li><li>餐厅：1800mm 实木餐桌 + 6 把真皮餐椅</li><li>主卧：1.8m 胡桃木床 + 双床头柜 + 6 门衣帽间</li></ul>",
            published_date=now - timedelta(days=30),
            sort=999,  # 置顶
            created_at=1, updated_at=1,
        ),
        CaseModel(
            title="现代北欧·佛山顺德120㎡三居室",
            category_id=space_bedroom.id,
            cover_url="https://images.unsplash.com/photo-1556909114-44e3e9399a2c?w=800",
            style="现代北欧",
            area="120㎡",
            description="<p>面向年轻夫妇的第一个家，预算 25 万。</p><p>整体采用浅色橡木 + 米白软装，搭配绿植点缀。</p>",
            published_date=now - timedelta(days=20),
            sort=998,
            created_at=1, updated_at=1,
        ),
        CaseModel(
            title="新中式·东莞东城复式楼",
            category_id=space_dining.id,
            cover_url="https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800",
            style="新中式",
            area="200㎡",
            description="<p>复式上下两层结构，下层以会客为主，上层为私密居住空间。</p>",
            published_date=now - timedelta(days=10),
            sort=997,
            created_at=1, updated_at=1,
        ),
    ]
    db.add_all(cases)
    db.flush()
    print(f"  ✓ 案例: 3 个（全部置顶）")

    # ----- 部门（树形：3 个节点） -----
    from app.models.dept import Dept as DeptModel

    # 先 ROOT
    root = DeptModel(
        name="YD 家居总部",
        code="YD",
        parent_id=None,
        sort=1,
        created_at=1, updated_at=1,
    )
    db.add(root)
    db.flush()
    root.path = f",{root.id},"

    sub_design = DeptModel(
        name="设计中心",
        code="DS",
        parent_id=root.id,
        sort=1,
        created_at=1, updated_at=1,
    )
    db.add(sub_design)
    db.flush()
    sub_design.path = f",{root.id},{sub_design.id},"

    sub_op = DeptModel(
        name="电商运营部",
        code="OPS",
        parent_id=root.id,
        sort=2,
        created_at=1, updated_at=1,
    )
    db.add(sub_op)
    db.flush()
    sub_op.path = f",{root.id},{sub_op.id},"

    print(f"  ✓ 部门: 3 个（1 总部 + 2 子部门）")

    db.commit()

print("\n✅ Lite 数据库初始化完成！")
print(f"   路径: {DB_FILE}")
print(f"   登录: admin / admin123")
