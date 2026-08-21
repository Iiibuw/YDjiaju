"""Schema bootstrap + 幂等种子数据。

- ensure_schema(): 以 ORM(Base.metadata)为唯一真相源,幂等建表。
  已存在的表不会重建,因此无论 MySQL 容器是否预置了 schema 都安全。
- seed_initial_data(db): 仅在 admin 不存在时写入演示数据,可重复调用。

Docker 部署时由 app.main 的 lifespan 调用;本地 Lite/MySQL 模式由
scripts/init_lite.py 调用,二者共用同一份种子逻辑,避免漂移。
"""
from datetime import datetime, timedelta

import app.models  # 触发 __init__ 注册全部 14 张表到 Base.metadata
from app.core.security import hash_password
from app.db.base import Base
from app.db import session


def ensure_schema() -> None:
    """幂等建表:已存在的表不会重建。"""
    # 确保全部模型已注册到 Base.metadata
    import app.models  # noqa: F401
    Base.metadata.create_all(bind=session.engine)


def seed_initial_data(db) -> bool:
    """幂等种子:admin 已存在则跳过整段(返回 False)。"""
    from app.models.admin_user import AdminUser

    if db.query(AdminUser).filter_by(username="admin").first():
        return False

    now = datetime.utcnow()

    # ----- 部门 -----
    tech_dept = _model("Dept", name="研发中心", code="RD", parent_id=None, sort=1, is_activate=1)
    db.add(tech_dept)
    db.flush()

    # ----- 角色（5 类 RBAC，对齐开发技术文档 §2.3.1 / 后台 ROLES 约定） -----
    role_specs = [
        ("admin", "超级管理员", "ALL", "内置超管", 1),
        ("editor", "内容编辑", "ALL", "内容与运营编辑", 2),
        ("product", "产品管理员", "ALL", "产品/分类/SKU 管理（产品全局共享，不做区域隔离）", 3),
        ("service", "客服主管", "REGION", "预约/留言/订单跟进", 4),
        ("order", "订单管理员", "REGION", "订单处理/发货", 5),
    ]
    roles_by_code = {}
    for code, name, scope, desc, sort in role_specs:
        r = _model("Role", name=name, code=code, data_scope=scope, description=desc, sort=sort, is_activate=1)
        db.add(r)
        db.flush()
        roles_by_code[code] = r
    admin_role = roles_by_code["admin"]

    # ----- 管理员 -----
    admin = _model(
        "AdminUser",
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

    # ----- 类目 -----
    space_dining = _model("Category", name="餐厅", kind="space", parent_id=None, sort=1, enabled=1)
    space_bedroom = _model("Category", name="卧室", kind="space", parent_id=None, sort=2, enabled=1)
    series_walnut = _model("Category", name="胡桃禮系列", kind="series", parent_id=None, sort=1, enabled=1)
    cat_table = _model("Category", name="餐桌", kind="category", parent_id=space_dining.id, sort=1, enabled=1)
    db.add_all([space_dining, space_bedroom, series_walnut, cat_table])
    db.flush()

    # ----- 产品 -----
    p1 = _model(
        "Product",
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
    p2 = _model(
        "Product",
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

    # ----- 资讯(5 条, 2 个分类) -----
    news_list = [
        _model(
            "News",
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
        _model(
            "News",
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
        _model(
            "News",
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
        _model(
            "News",
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
        _model(
            "News",
            title="胡桃禮系列新品发布会将于 10 月举行",
            subtitle="草稿预览",
            cover_url="https://images.unsplash.com/photo-1581539250439-c96689b5164a?w=800",
            summary="胡桃禮系列全新升级产品将于 10 月 1 日正式发布...",
            content="<p>胡桃禮系列全新升级产品将于 10 月 1 日正式发布，敬请期待。</p>",
            author="品牌部",
            category="company",
            view_count=0,
            is_published=0,
            is_top=0,
            is_recommend=0,
            sort=0,
            published_date=None,
            created_at=1, updated_at=1,
        ),
    ]
    db.add_all(news_list)
    db.flush()

    # ----- 招聘岗位(3 个) -----
    jobs = [
        _model(
            "Job",
            title="高级家具设计师",
            category="social",
            department="设计中心",
            location="佛山",
            salary_min_cents=1500000,
            salary_max_cents=2500000,
            headcount=2,
            description="<p>负责实木家具的产品设计与研发。</p>",
            requirement="<ul><li>5 年以上实木家具设计经验</li><li>熟练使用 SolidWorks/Rhino</li></ul>",
            publish_date=now - timedelta(days=2),
            expire_date=now + timedelta(days=60),
            created_at=1, updated_at=1,
        ),
        _model(
            "Job",
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
        _model(
            "Job",
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

    # ----- 案例(3 个) -----
    cases = [
        _model(
            "Case",
            title="胡桃禮·广州海珠湾花园别墅",
            category_id=space_dining.id,
            cover_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800",
            style="现代简约",
            area="280㎡",
            description="<p>客户为三代同堂的 6 口之家，整体调性强调温馨与品质感。</p><p>餐厅以胡桃禮实木餐桌为核心，搭配北美黑胡桃餐边柜，营造现代简约却温暖的就餐氛围。</p><h3>设计要点</h3><ul><li>客厅：胡桃木电视柜 + 真皮主沙发</li><li>餐厅：1800mm 实木餐桌 + 6 把真皮餐椅</li><li>主卧：1.8m 胡桃木床 + 双床头柜 + 6 门衣帽间</li></ul>",
            published_date=now - timedelta(days=30),
            sort=999,
            created_at=1, updated_at=1,
        ),
        _model(
            "Case",
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
        _model(
            "Case",
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

    # ----- 部门(树形: 3 个节点) -----
    root = _model("Dept", name="YD 家居总部", code="YD", parent_id=None, sort=1, created_at=1, updated_at=1)
    db.add(root)
    db.flush()
    root.path = f",{root.id},"

    sub_design = _model("Dept", name="设计中心", code="DS", parent_id=root.id, sort=1, created_at=1, updated_at=1)
    db.add(sub_design)
    db.flush()
    sub_design.path = f",{root.id},{sub_design.id},"

    sub_op = _model("Dept", name="电商运营部", code="OPS", parent_id=root.id, sort=2, created_at=1, updated_at=1)
    db.add(sub_op)
    db.flush()
    sub_op.path = f",{root.id},{sub_op.id},"

    # ----- 会员(2 个) -----
    m1 = _model(
        "User",
        phone="13800138001",
        password_hash=hash_password("member123"),
        nickname="张三",
        email="zhangsan@example.com",
        gender=1,
    )
    m2 = _model(
        "User",
        phone="13800138002",
        password_hash=hash_password("member123"),
        nickname="李四",
        email="lisi@example.com",
        gender=2,
    )
    db.add_all([m1, m2])
    db.flush()

    # ----- 留言(2 条) -----
    msg1 = _model("Message", name="王女士", phone="13900001111", content="请问胡桃禮餐桌可以定制尺寸吗？我家餐厅比较小。", status="pending")
    msg2 = _model("Message", name="陈先生", email="chen@example.com", content="想预约周末到佛山门店看沙发，请问营业时间是几点？", status="pending")
    db.add_all([msg1, msg2])
    db.flush()

    # ----- 订单(1 个 + 明细) -----
    o1 = _model(
        "Order",
        order_no="YD20260819001",
        user_id=m1.id,
        receiver_name="张三",
        receiver_phone="13800138001",
        receiver_address="广东省广州市天河区珠江新城花城大道 88 号",
        status="paid",
        total_cents=128000,
        shipping_cents=0,
        discount_cents=0,
        final_cents=128000,
        paid_date=now - timedelta(days=1),
        created_at=1, updated_at=1,
    )
    db.add(o1)
    db.flush()
    oi1 = _model(
        "OrderItem",
        order_id=o1.id,
        product_id=p1.id,
        product_name=p1.name,
        cover_url=p1.cover_url,
        price_cents=128000,
        quantity=1,
        subtotal_cents=128000,
        created_at=1, updated_at=1,
    )
    db.add(oi1)

    # ----- 预约(2 个) -----
    a1 = _model(
        "Appointment",
        user_id=m1.id,
        type="visit",
        name="张三",
        phone="13800138001",
        preferred_date=now + timedelta(days=3),
        message="想看看胡桃禮系列的餐桌和餐边柜。",
        status="pending",
        created_at=1, updated_at=1,
    )
    a2 = _model(
        "Appointment",
        type="custom",
        name="王女士",
        phone="13900001111",
        preferred_date=now + timedelta(days=5),
        message="想定制一张 2 米的黑胡桃木餐桌。",
        status="following",
        created_at=1, updated_at=1,
    )
    db.add_all([a1, a2])

    # ----- 权限点 + 角色授权（RBAC 基线，对齐开发技术文档 §2.3.1） -----
    perm_specs = [
        ("dashboard.view", "dashboard", "仪表盘查看"),
        ("product.view", "product", "产品查看"),
        ("product.create", "product", "产品新增"),
        ("product.edit", "product", "产品编辑"),
        ("product.delete", "product", "产品删除"),
        ("order.view", "order", "订单查看"),
        ("order.ship", "order", "订单发货"),
        ("order.refund", "order", "订单退款"),
        ("news.view", "news", "新闻查看"),
        ("news.create", "news", "新闻新增"),
        ("news.edit", "news", "新闻编辑"),
        ("news.delete", "news", "新闻删除"),
        ("case.view", "case", "案例查看"),
        ("case.create", "case", "案例新增"),
        ("case.edit", "case", "案例编辑"),
        ("case.delete", "case", "案例删除"),
        ("job.view", "job", "招聘查看"),
        ("job.edit", "job", "招聘编辑"),
        ("appointment.view", "appointment", "预约查看"),
        ("appointment.reply", "appointment", "预约跟进"),
        ("message.view", "message", "留言查看"),
        ("message.reply", "message", "留言回复"),
        ("user.view", "user", "会员查看"),
        ("dept.view", "dept", "部门查看"),
        ("dept.edit", "dept", "部门管理"),
        ("category.view", "category", "分类查看"),
        ("category.create", "category", "分类新增"),
        ("category.edit", "category", "分类编辑"),
        ("category.delete", "category", "分类删除"),
        ("banner.view", "banner", "轮播查看"),
        ("banner.create", "banner", "轮播新增"),
        ("banner.edit", "banner", "轮播编辑"),
        ("banner.delete", "banner", "轮播删除"),
        ("download.view", "download", "下载中心查看"),
        ("download.create", "download", "下载中心新增"),
        ("download.edit", "download", "下载中心编辑"),
        ("download.delete", "download", "下载中心删除"),
        ("about.view", "about", "关于我们查看"),
        ("about.create", "about", "关于我们新增"),
        ("about.edit", "about", "关于我们编辑"),
        ("about.delete", "about", "关于我们删除"),
        ("chat.view", "chat", "客服关键词查看"),
        ("chat.edit", "chat", "客服关键词编辑"),
        ("system.config", "system", "站点配置"),
        ("system.role", "system", "角色管理"),
        ("system.permission", "system", "权限管理"),
        ("system.audit", "system", "审计查看"),
    ]
    perms_by_code = {}
    for code, module, desc in perm_specs:
        p = _model("Permission", name=desc, code=code, module=module, description=desc, is_activate=1)
        db.add(p)
        db.flush()
        perms_by_code[code] = p

    # 授权：admin/editor 拥有全部；product/service/order 按原型 ROLES 精确授权（对齐 PRD §3.2 / §6.12）
    role_perms: dict[str, list[str]] = {
        "product": [
            "dashboard.view",
            "product.view", "product.create", "product.edit", "product.delete",
            "banner.view", "banner.create", "banner.edit", "banner.delete",
            "category.view", "order.view",
        ],
        "service": [
            "dashboard.view",
            "appointment.view", "appointment.reply",
            "message.view", "message.reply",
            "order.view",
        ],
        "order": [
            "dashboard.view",
            "order.view", "order.ship", "order.refund",
            "appointment.view", "appointment.reply",
        ],
    }
    for code, r in roles_by_code.items():
        if code in ("admin", "editor"):
            granted = list(perms_by_code.values())
        else:
            codes = role_perms.get(code, [])
            granted = [p for c, p in perms_by_code.items() if c in codes]
        for p in granted:
            db.add(_model("RolePermission", role_id=r.id, permission_id=p.id, is_activate=1))
    db.flush()

    db.commit()
    return True


def _model(cls_name: str, **kwargs):
    """按类名从已注册的模型中取类并实例化(延迟 import,确保 metadata 注册)。"""
    import app.models as M
    cls = getattr(M, cls_name)
    return cls(**kwargs)
