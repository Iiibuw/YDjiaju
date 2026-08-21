"""YD家居 数据库设计文档 ER 图生成器（v2 - 字段反转约定版）

输出：
  figures/db-ER-overview.svg          总览图（33 张表，含新增 depts）
  figures/db-ER-domain-01-auth.svg    用户与权限域详图（11 张表：原 10 + 新增 depts）

依赖：仅 Python 标准库。
约定：
  通用字段：id, is_activate, created_at(人), created_date(时间),
          updated_at(人), updated_date(时间)
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).parent

# ============== 配色（与开发技术文档 ER 图保持一致 + 微调）==============
C = {
    "bg":              "#FFFFFF",
    "text":            "#1F1F1F",
    "text_sub":        "#595959",
    "border":          "#D9D9D9",
    "border_strong":   "#8C8C8C",
    "edge":            "#8C8C8C",
    "edge_strong":     "#1F1F1F",
    "label_bg":        "#FFFFFF",
    # 用户权限域（紫色）
    "auth_fill":       "#F5F0FE",
    "auth_stroke":     "#7B5BD5",
    "auth_text":       "#2D1B6E",
    "auth_dark":       "#534AB7",
    # 部门表（紫色加深）
    "dept_fill":       "#E8DDFB",
    "dept_stroke":     "#5A3FB0",
    "dept_text":       "#1A0F4A",
    # 产品域（绿色）
    "prod_fill":       "#EAF3DE",
    "prod_stroke":     "#5B8F3F",
    "prod_text":       "#173404",
    # 内容域（蓝色）
    "con_fill":        "#E6F1FB",
    "con_stroke":      "#185FA5",
    "con_text":        "#042C53",
    # 招聘域（橙色）
    "rec_fill":        "#FAECE7",
    "rec_stroke":      "#993C1D",
    "rec_text":        "#4A1B0C",
    # 业务域（青色）
    "biz_fill":        "#E1F5EE",
    "biz_stroke":      "#0F6E56",
    "biz_text":        "#04342C",
    # 订单域（红色）
    "ord_fill":        "#FCEBEB",
    "ord_stroke":      "#A32D2D",
    "ord_text":        "#501313",
    # 统计域（灰色）
    "stat_fill":       "#F1EFE8",
    "stat_stroke":     "#5F5E5A",
    "stat_text":       "#2C2C2A",
}

# ============== 通用字段标注（顶部小标签栏）==============
COMMON_FIELDS_NOTE = [
    ("id",            "PK"),
    ("is_activate",   "激活"),
    ("created_at",    "创建人"),
    ("created_date",  "创建时间"),
    ("updated_at",    "修改人"),
    ("updated_date",  "修改时间"),
]

def common_field_line(prefix=""):
    """返回通用字段的简写注释行（用在 ER 图每个表的上方）"""
    return f"{prefix}<tspan fill='{C['text_sub']}' font-size='9'>通用：id / is_activate / created_at(人) / created_date / updated_at(人) / updated_date</tspan>"


def make_table_card(x, y, w, table_name, key_fields, fill, stroke, text_color, h=110, alias=None):
    """生成一张表卡片（矩形 + 顶部标题条 + 字段列表）"""
    title_h = 26
    parts = [
        f'<g transform="translate({x},{y})">',
        # 主框
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="6" ry="6" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>',
        # 标题条
        f'<rect x="0" y="0" width="{w}" height="{title_h}" rx="6" ry="6" '
        f'fill="{stroke}"/>',
        f'<rect x="0" y="{title_h-6}" width="{w}" height="6" '
        f'fill="{stroke}"/>',
        # 表名
        f'<text x="{w//2}" y="{title_h-9}" text-anchor="middle" '
        f'fill="#FFFFFF" font-size="12" font-weight="700" '
        f'font-family="monospace">{escape(table_name)}</text>',
    ]
    # 字段列表
    line_y = title_h + 14
    for field in key_fields[:6]:  # 最多显示 6 个字段
        parts.append(
            f'<text x="10" y="{line_y}" fill="{text_color}" font-size="10" '
            f'font-family="monospace">{escape(field)}</text>'
        )
        line_y += 13
    if len(key_fields) > 6:
        parts.append(
            f'<text x="10" y="{line_y}" fill="{text_color}" font-size="9" '
            f'font-style="italic" font-family="sans-serif">+ {len(key_fields)-6} fields...</text>'
        )
    parts.append('</g>')
    return "\n".join(parts)


def make_edge(x1, y1, x2, y2, label="", color=None, dashed=False):
    """生成连接线（带可选箭头与标签）"""
    if color is None:
        color = C["edge"]
    dash_attr = ' stroke-dasharray="4,3"' if dashed else ''
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="1.5"{dash_attr}/>',
    ]
    if label:
        parts.append(
            f'<rect x="{mid_x-18}" y="{mid_y-8}" width="36" height="14" '
            f'fill="{C["label_bg"]}" stroke="none"/>'
        )
        parts.append(
            f'<text x="{mid_x}" y="{mid_y+3}" text-anchor="middle" '
            f'fill="{color}" font-size="9" font-weight="600" '
            f'font-family="sans-serif">{escape(label)}</text>'
        )
    return "\n".join(parts)


# ============== 1) 总览 ER 图 ==============
def generate_overview():
    """33 张表按域分块布局的总览图"""
    W = 1180
    H = 800

    # 表定义（按 6 个域分组，每组相对位置）
    tables = {
        # 用户与权限域
        "users":             ("用户前台", ("id", "phone", "username"),     "auth"),
        "admin_users":       ("管理员",  ("id", "username", "real_name", "phone", "dept_id", "role_id", "post"), "auth"),
        "depts":             ("部门",    ("id", "name", "parent_id", "sort"), "dept"),
        "roles":             ("角色",    ("id", "name", "code", "data_scope"), "auth"),
        "admin_roles":       ("管理员-角色", ("admin_id", "role_id"),      "auth"),
        "admin_regions":     ("管理员-区域", ("admin_id", "region_code"),  "auth"),
        "user_addresses":    ("会员地址", ("id", "user_id", "region_code", "store_code"), "auth"),
        "user_favorites":    ("会员收藏", ("id", "user_id", "product_id"),  "auth"),
        "user_search_logs":  ("搜索记录", ("id", "user_id", "keyword"),     "auth"),
        "stats_visit":       ("访问日志", ("id", "path", "ip", "user_id"),  "stat"),
        # 产品域
        "categories":        ("分类",    ("id", "type", "name", "parent_id"), "prod"),
        "products":          ("产品",    ("id", "name", "series_id", "space_id", "category_id"), "prod"),
        "product_skus":      ("产品规格", ("id", "product_id", "spec_name", "price_cents"), "prod"),
        "product_images":    ("产品图片", ("id", "product_id", "url"),     "prod"),
        # 内容域
        "banners":           ("轮播图",  ("id", "title", "image_url", "sort"), "con"),
        "cases":             ("案例",    ("id", "title", "category_id"),  "con"),
        "case_images":       ("案例图集", ("id", "case_id", "url"),        "con"),
        "news":              ("新闻",    ("id", "title", "category", "publish_date"), "con"),
        "about_sections":    ("关于区块", ("id", "code", "title"),          "con"),
        "about_images":      ("关于图集", ("id", "section_id", "url"),      "con"),
        "downloads":         ("下载中心", ("id", "title", "category"),       "con"),
        "site_configs":      ("站点配置", ("id", "key", "value"),           "con"),
        "chat_keywords":     ("客服关键词", ("id", "keyword", "reply"),      "con"),
        # 招聘域
        "jobs":              ("岗位",    ("id", "title", "type", "location"), "rec"),
        "job_applications":  ("投递",    ("id", "job_id", "user_id", "stage", "phone", "region_code"), "rec"),
        # 业务域
        "appointments":      ("预约",    ("id", "name", "phone", "region_code", "store_code"), "biz"),
        "messages":          ("留言",    ("id", "name", "phone", "region_code", "store_code", "source"), "biz"),
        "cart_items":        ("购物车",  ("id", "user_id", "product_id"),  "biz"),
        # 订单域
        "orders":            ("订单",    ("id", "order_no", "user_id", "status", "final_cents", "region_code", "store_code"), "ord"),
        "order_items":       ("订单明细", ("id", "order_id", "product_id", "price_cents"), "ord"),
        "payments":          ("支付记录", ("id", "order_id", "amount_cents", "status"), "ord"),
    }

    # 域分块坐标
    zones = [
        ("用户与权限域",  "auth",  20, 60,  360, 360),
        ("产品域",        "prod",  400, 60, 280, 200),
        ("内容域",        "con",   400, 280, 280, 320),
        ("招聘域",        "rec",   700, 60, 240, 140),
        ("业务域",        "biz",   700, 220, 240, 200),
        ("订单域",        "ord",   700, 440, 240, 240),
    ]

    # 表的位置（按域内布局）
    cell_w = 116
    cell_h = 78

    # 通用辅助：返回 (cx, cy) 给连接线
    table_pos = {}

    def get_color(domain):
        return {
            "auth": (C["auth_fill"], C["auth_stroke"], C["auth_text"]),
            "dept": (C["dept_fill"], C["dept_stroke"], C["dept_text"]),
            "prod": (C["prod_fill"], C["prod_stroke"], C["prod_text"]),
            "con":  (C["con_fill"],  C["con_stroke"],  C["con_text"]),
            "rec":  (C["rec_fill"],  C["rec_stroke"],  C["rec_text"]),
            "biz":  (C["biz_fill"],  C["biz_stroke"],  C["biz_text"]),
            "ord":  (C["ord_fill"],  C["ord_stroke"],  C["ord_text"]),
            "stat": (C["stat_fill"], C["stat_stroke"], C["stat_text"]),
        }.get(domain, (C["auth_fill"], C["auth_stroke"], C["auth_text"]))

    # 域内布局函数：按表格数量决定列数
    layout_in_zone = {
        "用户与权限域": [
            ("users",              30,  30),
            ("admin_users",        155, 30),
            ("depts",              30,  125),
            ("roles",              155, 125),
            ("admin_roles",        280, 30),
            ("admin_regions",      280, 125),
            ("user_addresses",     30,  220),
            ("user_favorites",     155, 220),
            ("user_search_logs",   280, 220),
            ("stats_visit",        155, 315),
        ],
        "产品域": [
            ("categories",   20,  40),
            ("products",     140, 40),
            ("product_skus", 20,  135),
            ("product_images", 140, 135),
        ],
        "内容域": [
            ("banners",        20,  30),
            ("cases",          120, 30),
            ("case_images",    20,  115),
            ("news",           120, 115),
            ("about_sections", 20,  200),
            ("about_images",   120, 200),
            ("downloads",      20,  285),
            ("site_configs",   120, 285),
            ("chat_keywords",  20,  370),
        ],
        "招聘域": [
            ("jobs",              30,  40),
            ("job_applications",  30,  135),
        ],
        "业务域": [
            ("appointments",  30,  40),
            ("messages",      30,  135),
            ("cart_items",    30,  230),
        ],
        "订单域": [
            ("orders",      30,  40),
            ("order_items", 30,  135),
            ("payments",    30,  230),
        ],
    }

    body = []

    # 背景
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{C["bg"]}"/>')

    # 标题
    body.append(f'<text x="{W//2}" y="30" text-anchor="middle" fill="{C["text"]}" '
                f'font-size="20" font-weight="700" font-family="sans-serif">'
                f'YD家居 · ER 总览图（33 张表 / 6 大域）</text>')
    body.append(f'<text x="{W//2}" y="50" text-anchor="middle" fill="{C["text_sub"]}" '
                f'font-size="11" font-family="sans-serif">'
                f'字段反转约定：created_at=创建人, created_date=创建时间, updated_at=修改人, updated_date=修改时间, is_activate=激活/禁用'
                f'</text>')

    # 域块
    for zone_name, zone_key, zx, zy, zw, zh in zones:
        if zone_name == "用户与权限域":
            domain_color = C["auth_dark"]
        else:
            domain_color = get_color(zone_key)[1]

        # 域框
        body.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" ry="8" '
                    f'fill="none" stroke="{domain_color}" stroke-width="2" '
                    f'stroke-dasharray="6,4"/>')
        # 域标签
        body.append(f'<rect x="{zx+8}" y="{zy-10}" width="100" height="18" rx="3" ry="3" '
                    f'fill="{domain_color}"/>')
        body.append(f'<text x="{zx+58}" y="{zy+3}" text-anchor="middle" fill="#FFFFFF" '
                    f'font-size="11" font-weight="700" font-family="sans-serif">{zone_name}</text>')

        # 域内表
        layout = layout_in_zone.get(zone_name, [])
        for table_name, dx, dy in layout:
            if table_name not in tables:
                continue
            label, fields, domain = tables[table_name]
            fill, stroke, text_color = get_color(domain)
            tx = zx + dx
            ty = zy + dy
            table_pos[table_name] = (tx + cell_w//2, ty + cell_h//2)
            body.append(make_table_card(tx, ty, cell_w, table_name, fields, fill, stroke, text_color, h=cell_h))

    # 关键跨域外键关系（精选 ~12 条，避免图太乱）
    edges = [
        # 用户权限域 → 产品域
        ("user_favorites", "products", ""),
        ("cart_items", "products", ""),
        # 用户权限域 → 内容域
        ("user_search_logs", "news", ""),
        # 用户权限域 → 招聘域
        ("job_applications", "jobs", ""),
        ("job_applications", "users", "opt"),
        # 用户权限域 → 订单域
        ("orders", "users", ""),
        ("user_addresses", "users", ""),
        # 用户权限域 → 业务域
        ("appointments", "users", "opt"),
        ("messages", "users", "opt"),
        # 权限域内部
        ("admin_users", "depts", ""),
        ("admin_users", "roles", ""),
        ("admin_roles", "admin_users", ""),
        ("admin_roles", "roles", ""),
        # 产品域内部
        ("products", "categories", ""),
        ("product_skus", "products", ""),
        ("product_images", "products", ""),
        # 内容域内部
        ("case_images", "cases", ""),
        ("about_images", "about_sections", ""),
        # 招聘 → 用户
        # 订单域内部
        ("order_items", "orders", ""),
        ("payments", "orders", ""),
        ("order_items", "products", ""),
    ]

    for src, dst, label in edges:
        if src not in table_pos or dst not in table_pos:
            continue
        sx, sy = table_pos[src]
        dx, dy = table_pos[dst]
        body.append(make_edge(sx, sy, dx, dy, label, color=C["edge_strong"]))

    # 图例
    legend_y = H - 70
    body.append(f'<rect x="20" y="{legend_y}" width="{W-40}" height="56" rx="6" ry="6" '
                f'fill="none" stroke="{C["border"]}" stroke-width="1"/>')
    body.append(f'<text x="30" y="{legend_y+16}" fill="{C["text"]}" font-size="11" '
                f'font-weight="700" font-family="sans-serif">图例</text>')

    legend_items = [
        ("用户与权限域", C["auth_fill"], C["auth_stroke"]),
        ("部门表",       C["dept_fill"], C["dept_stroke"]),
        ("产品域",       C["prod_fill"], C["prod_stroke"]),
        ("内容域",       C["con_fill"],  C["con_stroke"]),
        ("招聘域",       C["rec_fill"],  C["rec_stroke"]),
        ("业务域",       C["biz_fill"],  C["biz_stroke"]),
        ("订单域",       C["ord_fill"],  C["ord_stroke"]),
    ]
    lx = 80
    for name, fill, stroke in legend_items:
        body.append(f'<rect x="{lx}" y="{legend_y+8}" width="14" height="14" rx="2" '
                    f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        body.append(f'<text x="{lx+20}" y="{legend_y+19}" fill="{C["text"]}" font-size="10" '
                    f'font-family="sans-serif">{name}</text>')
        lx += 110

    body.append(f'<text x="30" y="{legend_y+42}" fill="{C["text_sub"]}" font-size="9" '
                f'font-family="sans-serif">'
                f'通用字段（每张表均含）：id, is_activate（1=激活/0=禁用）, created_at（创建人 FK）, '
                f'created_date（创建时间 DATETIME(3)）, updated_at（修改人 FK）, updated_date（修改时间）'
                f'</text>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
        + "\n".join(body) +
        '\n</svg>'
    )

    out = OUT_DIR / "db-ER-overview.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"[OK] {out.name} ({len(svg)} bytes)")


# ============== 2) 用户与权限域 ER 图（详图）==============
def generate_auth_domain():
    """11 张表：users/admin_users/depts/roles/admin_roles/admin_regions
       user_addresses/user_favorites/user_search_logs/stats_visit + audit_logs
    """
    W = 1100
    H = 700

    tables = {
        # 子域 1：后台用户与权限
        "depts":             ("部门",    ("id", "name", "parent_id", "sort", "is_activate"),  "dept"),
        "admin_users":       ("管理员",  ("id", "username", "real_name", "phone", "dept_id", "role_id", "post", "is_activate"), "auth"),
        "roles":             ("角色",    ("id", "name", "code", "data_scope", "is_activate"), "auth"),
        "admin_roles":       ("管理员-角色", ("admin_id", "role_id", "is_activate"),       "auth"),
        "admin_regions":     ("管理员-区域", ("admin_id", "region_code"),                 "auth"),
        "permissions":       ("权限点",   ("id", "code", "name", "module", "is_activate"), "auth"),
        "role_permissions":  ("角色-权限", ("role_id", "permission_id"),                 "auth"),
        # 子域 2：前台会员
        "users":             ("会员",    ("id", "phone", "nickname", "is_activate"),      "auth"),
        "user_addresses":    ("会员地址", ("id", "user_id", "name", "phone", "region_code", "store_code", "is_default", "is_activate"), "auth"),
        "user_favorites":    ("会员收藏", ("id", "user_id", "product_id", "is_activate"),  "auth"),
        "user_search_logs":  ("搜索记录", ("id", "user_id", "keyword", "result_count"),   "auth"),
        # 子域 3：审计与日志
        "stats_visit":       ("访问日志", ("id", "user_id", "path", "ip", "created_date"), "stat"),
    }

    # 布局：3 个子域横向排列
    sub_zones = [
        ("后台用户 · 角色 · 权限", 20, 80, 660, 540, "back"),
        ("前台会员域",             700, 80, 380, 540, "front"),
    ]

    back_layout = [
        ("depts",            20,  40),
        ("admin_users",      150, 40),
        ("roles",            290, 40),
        ("permissions",      430, 40),
        ("admin_roles",      20,  200),
        ("role_permissions", 150, 200),
        ("admin_regions",    290, 200),
    ]

    front_layout = [
        ("users",              30,  40),
        ("user_addresses",     150, 40),
        ("user_favorites",     30,  175),
        ("user_search_logs",   150, 175),
        ("stats_visit",        30,  310),
    ]

    cell_w = 130
    cell_h = 110

    def get_color(domain):
        return {
            "auth": (C["auth_fill"], C["auth_stroke"], C["auth_text"]),
            "dept": (C["dept_fill"], C["dept_stroke"], C["dept_text"]),
            "stat": (C["stat_fill"], C["stat_stroke"], C["stat_text"]),
        }.get(domain, (C["auth_fill"], C["auth_stroke"], C["auth_text"]))

    table_pos = {}

    body = []
    body.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{C["bg"]}"/>')

    # 标题
    body.append(f'<text x="{W//2}" y="30" text-anchor="middle" fill="{C["text"]}" '
                f'font-size="20" font-weight="700" font-family="sans-serif">'
                f'YD家居 · 用户与权限域 ER 详图（含部门表）</text>')
    body.append(f'<text x="{W//2}" y="52" text-anchor="middle" fill="{C["text_sub"]}" '
                f'font-size="11" font-family="sans-serif">'
                f'后台用户/角色/权限 + 前台会员 + 审计日志 · 字段约定（created_at=人, created_date=时间, is_activate=激活）'
                f'</text>')

    # 子域 1: 后台
    zx, zy, zw, zh = sub_zones[0][1:5]
    body.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" ry="8" '
                f'fill="none" stroke="{C["auth_stroke"]}" stroke-width="2" stroke-dasharray="6,4"/>')
    body.append(f'<rect x="{zx+8}" y="{zy-10}" width="200" height="18" rx="3" ry="3" '
                f'fill="{C["auth_stroke"]}"/>')
    body.append(f'<text x="{zx+108}" y="{zy+3}" text-anchor="middle" fill="#FFFFFF" '
                f'font-size="11" font-weight="700" font-family="sans-serif">{sub_zones[0][0]}</text>')

    for table_name, dx, dy in back_layout:
        if table_name not in tables:
            continue
        label, fields, domain = tables[table_name]
        fill, stroke, text_color = get_color(domain)
        tx = zx + dx
        ty = zy + dy
        table_pos[table_name] = (tx + cell_w//2, ty + cell_h//2)
        body.append(make_table_card(tx, ty, cell_w, table_name, fields, fill, stroke, text_color, h=cell_h))

    # 子域 2: 前台
    zx, zy, zw, zh = sub_zones[1][1:5]
    body.append(f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="8" ry="8" '
                f'fill="none" stroke="{C["auth_stroke"]}" stroke-width="2" stroke-dasharray="6,4"/>')
    body.append(f'<rect x="{zx+8}" y="{zy-10}" width="120" height="18" rx="3" ry="3" '
                f'fill="{C["auth_stroke"]}"/>')
    body.append(f'<text x="{zx+68}" y="{zy+3}" text-anchor="middle" fill="#FFFFFF" '
                f'font-size="11" font-weight="700" font-family="sans-serif">{sub_zones[1][0]}</text>')

    for table_name, dx, dy in front_layout:
        if table_name not in tables:
            continue
        label, fields, domain = tables[table_name]
        fill, stroke, text_color = get_color(domain)
        tx = zx + dx
        ty = zy + dy
        table_pos[table_name] = (tx + cell_w//2, ty + cell_h//2)
        body.append(make_table_card(tx, ty, cell_w, table_name, fields, fill, stroke, text_color, h=cell_h))

    # 关键关系
    edges = [
        ("admin_users", "depts", ""),
        ("admin_users", "roles", ""),
        ("admin_roles", "admin_users", ""),
        ("admin_roles", "roles", ""),
        ("admin_regions", "admin_users", ""),
        ("role_permissions", "roles", ""),
        ("role_permissions", "permissions", ""),
        ("user_addresses", "users", ""),
        ("user_favorites", "users", ""),
        ("user_search_logs", "users", ""),
        ("stats_visit", "users", "opt"),
    ]

    for src, dst, label in edges:
        if src not in table_pos or dst not in table_pos:
            continue
        sx, sy = table_pos[src]
        dx, dy = table_pos[dst]
        body.append(make_edge(sx, sy, dx, dy, label, color=C["edge_strong"]))

    # 图例
    legend_y = H - 70
    body.append(f'<rect x="20" y="{legend_y}" width="{W-40}" height="56" rx="6" ry="6" '
                f'fill="none" stroke="{C["border"]}" stroke-width="1"/>')
    body.append(f'<text x="30" y="{legend_y+16}" fill="{C["text"]}" font-size="11" '
                f'font-weight="700" font-family="sans-serif">图例</text>')

    legend_items = [
        ("后台用户/权限", C["auth_fill"], C["auth_stroke"]),
        ("部门表",       C["dept_fill"], C["dept_stroke"]),
        ("统计/日志",     C["stat_fill"], C["stat_stroke"]),
    ]
    lx = 130
    for name, fill, stroke in legend_items:
        body.append(f'<rect x="{lx}" y="{legend_y+8}" width="14" height="14" rx="2" '
                    f'fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
        body.append(f'<text x="{lx+20}" y="{legend_y+19}" fill="{C["text"]}" font-size="10" '
                    f'font-family="sans-serif">{name}</text>')
        lx += 150

    body.append(f'<text x="30" y="{legend_y+42}" fill="{C["text_sub"]}" font-size="9" '
                f'font-family="sans-serif">'
                f'通用字段（每张表均含）：id, is_activate, created_at(人), created_date, updated_at(人), updated_date · '
                f'虚线 = 可选外键（如 user_id 可为 NULL）'
                f'</text>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid meet">\n'
        + "\n".join(body) +
        '\n</svg>'
    )

    out = OUT_DIR / "db-ER-domain-01-auth.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"[OK] {out.name} ({len(svg)} bytes)")


if __name__ == "__main__":
    generate_overview()
    generate_auth_domain()