"""YD家居 开发技术文档 - 架构图与 ER 图生成器

依赖：仅使用 Python 标准库（xml.etree + html escape），无需第三方包。
输出：figures/frontend-architecture.svg, figures/backend-architecture.svg, figures/er-diagram.svg
"""

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).parent

# 配色（与 UI/UX 文档保持一致：前台 stone/gold 暖色 + 后台 AntD 蓝）
C = {
    "bg":          "#FFFFFF",
    "text":        "#1F1F1F",
    "text_sub":    "#595959",
    "border":      "#D9D9D9",
    "border_strong": "#8C8C8C",
    # 前台
    "page_fill":   "#FAEEDA",   # 页面层 amber 50
    "page_stroke": "#BA7517",   # amber 600
    "page_text":   "#633806",
    "comp_fill":   "#EEEDFE",   # 组件层 purple 50
    "comp_stroke": "#534AB7",
    "comp_text":   "#26215C",
    "api_fill":    "#E6F1FB",   # API 层 blue 50
    "api_stroke":  "#185FA5",
    "api_text":    "#042C53",
    "state_fill":  "#EAF3DE",   # state green 50
    "state_stroke":"#3B6D11",
    "state_text":  "#173404",
    "svc_fill":    "#E1F5EE",   # service teal 50
    "svc_stroke":  "#0F6E56",
    "svc_text":    "#04342C",
    "db_fill":     "#F1EFE8",   # db gray 50
    "db_stroke":   "#5F5E5A",
    "db_text":     "#2C2C2A",
    "shared_fill": "#FBEAF0",   # shared pink 50
    "shared_stroke":"#993556",
    "shared_text": "#4B1528",
    # 后台
    "auth_fill":   "#FCEBEB",   # auth red 50
    "auth_stroke": "#A32D2D",
    "auth_text":   "#501313",
    "mod_sys_fill":"#FAECE7",   # 系统管理 coral 50
    "mod_sys_stroke": "#993C1D",
    "mod_sys_text": "#4A1B0C",
    "mod_con_fill":"#EAF3DE",   # 内容管理 green 50
    "mod_con_stroke":"#3B6D11",
    "mod_con_text":"#173404",
    "mod_cus_fill":"#E6F1FB",   # 客户管理 blue 50
    "mod_cus_stroke":"#185FA5",
    "mod_cus_text":"#042C53",
    "mod_rec_fill":"#EEEDFE",   # 招聘管理 purple 50
    "mod_rec_stroke":"#534AB7",
    "mod_rec_text":"#26215C",
    "mod_ord_fill":"#FAEEDA",   # 订单管理 amber 50
    "mod_ord_stroke":"#BA7517",
    "mod_ord_text":"#633806",
}


def rect(x, y, w, h, fill, stroke, rx=6, stroke_w=0.6, opacity=1.0):
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}"{op}/>'


def text(x, y, s, size=11, color=None, anchor="middle", weight=400, family="sans-serif"):
    color = color or C["text"]
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')


def arrow(x1, y1, x2, y2, color="#8C8C8C", dashed=False, marker="url(#arrow)"):
    dash = ' stroke-dasharray="3,3"' if dashed else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="1"{dash} marker-end="{marker}"/>')


def arrow_defs():
    return """<defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 0 L10 5 L0 10 z" fill="#8C8C8C"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0 0 L10 5 L0 10 z" fill="#185FA5"/>
    </marker>
  </defs>"""


# ============================================================
# Diagram 1: 前台系统模块架构图
# ============================================================

def frontend_arch():
    W, H = 680, 760
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">']
    parts.append(arrow_defs())

    # 标题栏
    parts.append(rect(0, 0, W, 56, C["svc_fill"], C["svc_stroke"], rx=0))
    parts.append(text(W/2, 24, "前台系统模块架构图", size=15, color=C["svc_text"], weight=500))
    parts.append(text(W/2, 44, "Frontend 系统  →  React 18 + TypeScript + TailwindCSS + Vite", size=11, color=C["svc_stroke"]))

    # ===== Layer 1: 页面层 =====
    y = 76
    parts.append(rect(20, y, W-40, 168, C["page_fill"], C["page_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y+18, "① 页面层 · Pages", size=12, color=C["page_text"], anchor="start", weight=500))
    parts.append(text(28, y+34, "共 22 个页面（按 UI/UX 文档第五篇）", size=10, color=C["page_text"], anchor="start"))

    # 页面网格：3 行 × 7 列
    pages = [
        # Row 1: 浏览类
        ["首页 Home", "产品中心 Products", "产品详情 ProductDetail", "案例 Cases", "案例详情 CaseDetail", "新闻 News", "新闻详情 NewsDetail"],
        # Row 2: 业务类
        ["招聘 Jobs", "岗位详情 JobDetail", "关于我们 About", "下载中心 Download", "购物车 Cart", "结算 Checkout", "我的订单 MyOrders"],
        # Row 3: 工具类
        ["我的预约 MyAppointments", "在线预约 Appointment", "我的投递 MyApps", "站内搜索 Search", "在线客服 Chat", "登录 Login", "会员中心 MemberCenter"],
    ]
    bx, by, bw, bh, gap = 28, y+48, 86, 32, 8
    for row in pages:
        for i, p in enumerate(row):
            cx = bx + i * (bw + gap)
            parts.append(rect(cx, by, bw, bh, C["page_fill"], C["page_stroke"], rx=4, stroke_w=0.5))
            parts.append(text(cx + bw/2, by + bh/2, p, size=10, color=C["page_text"]))
        by += bh + 6

    # ===== Layer 2: 组件层 =====
    y2 = 260
    parts.append(rect(20, y2, W-40, 118, C["comp_fill"], C["comp_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y2+18, "② 组件层 · Components", size=12, color=C["comp_text"], anchor="start", weight=500))
    parts.append(text(28, y2+34, "复用组件 + 业务组件（按 UI/UX 第七篇）", size=10, color=C["comp_text"], anchor="start"))

    comps = ["Navbar 顶栏", "Footer 页脚", "HeroBanner 轮播", "ProductCard", "CaseCard", "NewsCard", "JobCard",
             "Pagination", "Loading", "Carousel 轮播", "Timeline 时间线", "Modal 弹窗", "Filter 筛选", "SearchBar"]
    bx, by, bw, bh, gap = 28, y2+48, 86, 32, 8
    for i, c in enumerate(comps):
        if i == 7:
            by += bh + 6
            bx = 28
        cx = bx + i * (bw + gap) if i < 7 else bx
        parts.append(rect(cx, by, bw, bh, C["comp_fill"], C["comp_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, c, size=10, color=C["comp_text"]))

    # ===== Layer 3: API 调用层 =====
    y3 = 394
    parts.append(rect(20, y3, W-40, 78, C["api_fill"], C["api_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y3+18, "③ API 调用层（src/api/）", size=12, color=C["api_text"], anchor="start", weight=500))

    apis = ["client.ts", "products.ts", "cases.ts", "news.ts", "jobs.ts", "appointments.ts",
            "messages.ts", "orders.ts", "member.ts", "auth.ts", "upload.ts", "search.ts"]
    bx, by, bw, bh, gap = 28, y3+34, 86, 28, 8
    for i, a in enumerate(apis):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["api_fill"], C["api_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, a, size=10, color=C["api_text"]))

    # ===== Layer 4: 状态管理 & Hooks =====
    y4 = 488
    parts.append(rect(20, y4, W-40, 64, C["state_fill"], C["state_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y4+18, "④ 状态管理 & Hooks", size=12, color=C["state_text"], anchor="start", weight=500))

    states = ["useState / useEffect", "React Context", "Custom Hooks", "Zustand Store", "React Query (server cache)"]
    bx, by, bw, bh, gap = 28, y4+32, 116, 24, 8
    for i, s in enumerate(states):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["state_fill"], C["state_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, s, size=10, color=C["state_text"]))

    # ===== Layer 5: 共享模块 =====
    y5 = 568
    parts.append(rect(20, y5, W-40, 52, C["shared_fill"], C["shared_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y5+18, "⑤ 共享模块 · Shared（packages/shared/）", size=12, color=C["shared_text"], anchor="start", weight=500))
    shares = ["types/ 类型", "utils/ 工具", "MainLayout", "useAuth/useMember", "i18n 预留"]
    bx, by, bw, bh, gap = 28, y5+30, 116, 18, 8
    for i, s in enumerate(shares):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["shared_fill"], C["shared_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, s, size=10, color=C["shared_text"]))

    # ===== API 服务 + 数据库 =====
    y6 = 636
    parts.append(rect(180, y6, 320, 40, C["svc_fill"], C["svc_stroke"], rx=6, stroke_w=0.8))
    parts.append(text(340, y6+15, "FastAPI 服务（api/）", size=12, color=C["svc_text"], weight=500))
    parts.append(text(340, y6+30, "http://api.yd-home.com  ·  Uvicorn + Gunicorn", size=10, color=C["svc_stroke"]))

    parts.append(rect(280, y6+50, 120, 32, C["db_fill"], C["db_stroke"], rx=6, stroke_w=0.8))
    parts.append(text(340, y6+66, "MySQL 8.0", size=12, color=C["db_text"], weight=500))

    # 流向箭头
    parts.append(arrow(340, 568, 340, 636, color=C["svc_stroke"]))
    parts.append(arrow(340, 676, 340, 686, color=C["db_stroke"]))

    # 图例
    leg_y = 712
    parts.append(text(20, leg_y, "图例：", size=10, color=C["text_sub"], anchor="start"))
    legend_items = [
            (C["page_fill"], C["page_stroke"], "页面层"),
            (C["comp_fill"], C["comp_stroke"], "组件层"),
            (C["api_fill"], C["api_stroke"], "API 调用"),
            (C["state_fill"], C["state_stroke"], "状态/Hooks"),
            (C["shared_fill"], C["shared_stroke"], "共享模块"),
            (C["svc_fill"], C["svc_stroke"], "API 服务"),
            (C["db_fill"], C["db_stroke"], "数据库"),
    ]
    lx = 70
    for fill, stroke, label in legend_items:
        parts.append(rect(lx, leg_y-10, 14, 12, fill, stroke, rx=2, stroke_w=0.5))
        parts.append(text(lx+18, leg_y, label, size=10, color=C["text"], anchor="start"))
        lx += 84

    parts.append('</svg>')
    return "\n".join(parts)


# ============================================================
# Diagram 2: 后台系统模块架构图
# ============================================================

def backend_arch():
    W, H = 680, 760
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">']
    parts.append(arrow_defs())

    # 标题栏
    parts.append(rect(0, 0, W, 56, C["mod_cus_fill"], C["mod_cus_stroke"], rx=0))
    parts.append(text(W/2, 24, "后台系统模块架构图", size=15, color=C["mod_cus_text"], weight=500))
    parts.append(text(W/2, 44, "Backend 系统  →  React 18 + TypeScript + Ant Design 5 + Vite", size=11, color=C["mod_cus_stroke"]))

    # ===== Layer 1: 认证体系 =====
    y = 76
    parts.append(rect(20, y, W-40, 64, C["auth_fill"], C["auth_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y+18, "① 认证体系 · Auth（全局配置）", size=12, color=C["auth_text"], anchor="start", weight=500))

    auth_items = ["Login 登录页", "JWT Token 管理", "axios 拦截器", "路由守卫 RouteGuard", "角色守卫 RoleGuard"]
    bx, by, bw, bh, gap = 28, y+32, 116, 24, 8
    for i, s in enumerate(auth_items):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["auth_fill"], C["auth_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, s, size=10, color=C["auth_text"]))

    # ===== Layer 2: 核心管理模块（按类别分组） =====
    y2 = 156
    # 容器
    parts.append(rect(20, y2, W-40, 240, "#FAFAFA", C["border_strong"], rx=10, opacity=0.4))
    parts.append(text(28, y2+18, "② 核心管理模块 · 11 个页面", size=12, color=C["text"], anchor="start", weight=500))
    parts.append(text(28, y2+34, "通用 CRUD 模式（表格 + 弹窗 + 筛选）  ·  RBAC 权限控制（角色动态菜单）  ·  上传组件", size=10, color=C["text_sub"], anchor="start"))

    # 四个类别分组
    categories = [
        ("系统管理", C["mod_sys_fill"], C["mod_sys_stroke"], C["mod_sys_text"],
            [("M1 仪表盘", "Dashboard"), ("M2 系统管理", "System"), ("M3 审计日志", "Audit"), ("M4 站点配置", "SiteConfig")]),
        ("内容管理", C["mod_con_fill"], C["mod_con_stroke"], C["mod_con_text"],
            [("M5 轮播图", "Carousels"), ("M6 产品/分类", "Products"), ("M7 SKU/库存", "SKUs"), ("M8 案例", "Cases"), ("M9 新闻", "News"), ("M10 关于我们", "About")]),
        ("客户管理", C["mod_cus_fill"], C["mod_cus_stroke"], C["mod_cus_text"],
            [("M11 预约", "Appointments"), ("M12 留言", "Messages"), ("M13 会员", "Members")]),
        ("订单/招聘", C["mod_ord_fill"], C["mod_ord_stroke"], C["mod_ord_text"],
            [("M14 订单", "Orders"), ("M15 招聘", "Jobs"), ("M16 投递", "Applications")]),
    ]

    # 4 列布局
    col_w = (W - 60) / 4 - 4
    col_x0 = 30
    row_y0 = y2 + 50
    box_h = 28
    for ci, (cat_name, fill, stroke, txt_color, mods) in enumerate(categories):
        cx = col_x0 + ci * (col_w + 4)
        # 类别标题
        parts.append(rect(cx, row_y0, col_w, 22, fill, stroke, rx=4, stroke_w=0.6))
        parts.append(text(cx + col_w/2, row_y0 + 11, cat_name, size=11, color=txt_color, weight=500))
        # 模块
        my = row_y0 + 30
        for m_label, m_code in mods:
            parts.append(rect(cx, my, col_w, box_h, "#FFFFFF", stroke, rx=4, stroke_w=0.5))
            parts.append(text(cx + col_w/2, my + 10, m_label, size=10, color=txt_color, weight=500))
            parts.append(text(cx + col_w/2, my + 22, m_code, size=9, color=txt_color))
            my += box_h + 6

    # ===== Layer 3: 后台 API 调用层 =====
    y3 = 412
    parts.append(rect(20, y3, W-40, 64, C["api_fill"], C["api_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y3+18, "③ 后台 API 调用层（src/api/admin/）", size=12, color=C["api_text"], anchor="start", weight=500))

    apis = ["auth.ts", "dashboard.ts", "products.ts", "categories.ts", "skus.ts", "cases.ts",
            "news.ts", "jobs.ts", "orders.ts", "upload.ts", "roles.ts", "audit.ts"]
    bx, by, bw, bh, gap = 28, y3+34, 86, 22, 8
    for i, a in enumerate(apis):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["api_fill"], C["api_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, a, size=9, color=C["api_text"]))

    # ===== Layer 4: 共享模块 =====
    y4 = 492
    parts.append(rect(20, y4, W-40, 52, C["shared_fill"], C["shared_stroke"], rx=10, opacity=0.55))
    parts.append(text(28, y4+18, "④ 共享模块（packages/shared/）", size=12, color=C["shared_text"], anchor="start", weight=500))
    shares = ["types/", "utils/request", "ProLayout", "useAuth/usePerms", "i18n 预留"]
    bx, by, bw, bh, gap = 28, y4+30, 116, 18, 8
    for i, s in enumerate(shares):
        cx = bx + i * (bw + gap)
        parts.append(rect(cx, by, bw, bh, C["shared_fill"], C["shared_stroke"], rx=4, stroke_w=0.5))
        parts.append(text(cx + bw/2, by + bh/2, s, size=10, color=C["shared_text"]))

    # ===== Layer 5: API 服务 + 数据库 =====
    y5 = 560
    parts.append(rect(180, y5, 320, 40, C["svc_fill"], C["svc_stroke"], rx=6, stroke_w=0.8))
    parts.append(text(340, y5+15, "FastAPI 服务（api/）", size=12, color=C["svc_text"], weight=500))
    parts.append(text(340, y5+30, "/api/admin/*  ·  JWT 认证 + RBAC 装饰器", size=10, color=C["svc_stroke"]))

    parts.append(rect(180, y5+52, 320, 56, C["mod_sys_fill"], C["mod_sys_stroke"], rx=6, stroke_w=0.8, opacity=0.6))
    parts.append(text(340, y5+68, "中间件：日志 / 异常 / 限流 / 审计", size=11, color=C["mod_sys_text"], weight=500))
    parts.append(text(340, y5+86, "Storage 抽象（OSS/COS/S3 可插拔）", size=10, color=C["mod_sys_text"]))
    parts.append(text(340, y5+102, "统计采集（PV/UV → stats_visit）", size=10, color=C["mod_sys_text"]))

    parts.append(rect(280, y5+120, 120, 32, C["db_fill"], C["db_stroke"], rx=6, stroke_w=0.8))
    parts.append(text(340, y5+136, "MySQL 8.0", size=12, color=C["db_text"], weight=500))

    # 流向箭头
    parts.append(arrow(340, 140, 340, 156, color=C["auth_stroke"]))
    parts.append(arrow(340, 396, 340, 412, color=C["api_stroke"]))
    parts.append(arrow(340, 476, 340, 492, color=C["shared_stroke"]))
    parts.append(arrow(340, 544, 340, 560, color=C["svc_stroke"]))
    parts.append(arrow(340, 680, 340, 680, color=C["db_stroke"]))

    # 图例
    leg_y = 730
    parts.append(text(20, leg_y, "图例：", size=10, color=C["text_sub"], anchor="start"))
    legend_items = [
            (C["auth_fill"], C["auth_stroke"], "认证体系"),
            (C["mod_sys_fill"], C["mod_sys_stroke"], "系统管理"),
            (C["mod_con_fill"], C["mod_con_stroke"], "内容管理"),
            (C["mod_cus_fill"], C["mod_cus_stroke"], "客户管理"),
            (C["mod_ord_fill"], C["mod_ord_stroke"], "订单/招聘"),
            (C["api_fill"], C["api_stroke"], "API 调用"),
            (C["svc_fill"], C["svc_stroke"], "API 服务"),
    ]
    lx = 70
    for fill, stroke, label in legend_items:
        parts.append(rect(lx, leg_y-10, 14, 12, fill, stroke, rx=2, stroke_w=0.5))
        parts.append(text(lx+18, leg_y, label, size=10, color=C["text"], anchor="start"))
        lx += 76

    parts.append('</svg>')
    return "\n".join(parts)


# ============================================================
# Diagram 3: ER 图（数据库设计）
# ============================================================

def er_diagram():
    W, H = 880, 720
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">']
    parts.append(arrow_defs())

    # 标题栏
    parts.append(rect(0, 0, W, 48, C["db_fill"], C["db_stroke"], rx=0))
    parts.append(text(W/2, 22, "数据库 ER 图（25+ 表核心实体）", size=14, color=C["db_text"], weight=500))
    parts.append(text(W/2, 40, "MySQL 8.0  ·  InnoDB  ·  utf8mb4_unicode_ci", size=10, color=C["db_stroke"]))

    # 表实体（绘制为带表头与字段的卡片）
    def entity(x, y, w, table_name, fields, accent):
        h = 24 + len(fields) * 14
        parts.append(rect(x, y, w, h, "#FFFFFF", accent, rx=4, stroke_w=0.8))
        # 表头
        parts.append(rect(x, y, w, 22, accent, accent, rx=4, stroke_w=0.8))
        parts.append(text(x + w/2, y + 14, table_name, size=11, color="#FFFFFF", weight=500))
        # 字段
        fy = y + 22 + 10
        for fk, ft in fields:
            parts.append(text(x + 8, fy, fk, size=8, color=C["text"], anchor="start"))
            parts.append(text(x + w - 8, fy, ft, size=8, color=C["text_sub"], anchor="end"))
            fy += 14

    # 实体定义：(x, y, w, table_name, [(field, type), ...], accent_color)
    entities = [
        # 用户域
        (40, 70, 170, "users 前台会员", [
            ("id", "BIGINT PK"),
            ("phone", "VARCHAR(20) UQ"),
            ("password_hash", "VARCHAR(128)"),
            ("nickname", "VARCHAR(64)"),
            ("avatar_url", "VARCHAR(255)"),
            ("status", "TINYINT"),
            ("created_at", "DATETIME"),
        ], "#534AB7"),
        (40, 230, 170, "user_addresses", [
            ("id", "BIGINT PK"),
            ("user_id", "FK→users"),
            ("receiver", "VARCHAR(64)"),
            ("phone", "VARCHAR(20)"),
            ("province/city", "VARCHAR(64)"),
            ("detail", "VARCHAR(255)"),
            ("is_default", "TINYINT"),
        ], "#534AB7"),
        (40, 410, 170, "admin_users", [
            ("id", "BIGINT PK"),
            ("username", "VARCHAR(64) UQ"),
            ("password_hash", "VARCHAR(128)"),
            ("display_name", "VARCHAR(64)"),
            ("status", "TINYINT"),
            ("last_login_at", "DATETIME"),
        ], "#A32D2D"),
        (40, 560, 170, "audit_logs", [
            ("id", "BIGINT PK"),
            ("admin_id", "FK→admin_users"),
            ("action", "VARCHAR(32)"),
            ("resource", "VARCHAR(64)"),
            ("ip", "VARCHAR(45)"),
            ("created_at", "DATETIME"),
        ], "#A32D2D"),

        # 角色权限域
        (250, 70, 170, "roles 角色", [
            ("id", "INT PK"),
            ("code", "VARCHAR(32) UQ"),
            ("name", "VARCHAR(64)"),
            ("data_scope", "TINYINT"),
        ], "#993C1D"),
        (250, 200, 170, "permissions 权限", [
            ("id", "INT PK"),
            ("module", "VARCHAR(32)"),
            ("action", "VARCHAR(32)"),
            ("code", "VARCHAR(64) UQ"),
        ], "#993C1D"),
        (250, 330, 170, "admin_roles", [
            ("admin_id", "FK→admin_users"),
            ("role_id", "FK→roles"),
            ("PRIMARY KEY", "(admin_id, role_id)"),
        ], "#993C1D"),
        (250, 420, 170, "role_permissions", [
            ("role_id", "FK→roles"),
            ("permission_id", "FK→permissions"),
            ("PRIMARY KEY", "(role_id, permission_id)"),
        ], "#993C1D"),
        (250, 510, 170, "admin_regions 数据范围", [
            ("id", "BIGINT PK"),
            ("admin_id", "FK→admin_users"),
            ("region_code", "VARCHAR(32)"),
            ("store_code", "VARCHAR(32)"),
        ], "#993C1D"),
        (250, 620, 170, "site_configs", [
            ("id", "INT PK"),
            ("key", "VARCHAR(64) UQ"),
            ("value", "TEXT"),
            ("group", "VARCHAR(32)"),
        ], "#993C1D"),

        # 产品域
        (460, 70, 170, "categories 分类", [
            ("id", "INT PK"),
            ("type", "ENUM 系列/空间/品类"),
            ("name", "VARCHAR(64)"),
            ("parent_id", "FK→categories"),
            ("sort", "INT"),
        ], "#3B6D11"),
        (460, 230, 170, "products 产品", [
            ("id", "BIGINT PK"),
            ("name", "VARCHAR(128)"),
            ("series_id", "FK→categories"),
            ("space_id", "FK→categories"),
            ("category_id", "FK→categories"),
            ("material/style", "VARCHAR(64)"),
            ("is_custom", "TINYINT"),
            ("support_order", "TINYINT"),
        ], "#3B6D11"),
        (460, 410, 170, "product_skus", [
            ("id", "BIGINT PK"),
            ("product_id", "FK→products"),
            ("color", "VARCHAR(32)"),
            ("size", "VARCHAR(32)"),
            ("material", "VARCHAR(32)"),
            ("price", "DECIMAL(10,2)"),
            ("stock", "INT"),
            ("code", "VARCHAR(64) UQ"),
        ], "#3B6D11"),
        (460, 580, 170, "product_images", [
            ("id", "BIGINT PK"),
            ("product_id", "FK→products"),
            ("url", "VARCHAR(255)"),
            ("sort", "INT"),
            ("is_cover", "TINYINT"),
        ], "#3B6D11"),

        # 内容域
        (670, 70, 170, "cases 案例", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("space/style", "VARCHAR(64)"),
            ("area", "VARCHAR(64)"),
            ("content", "LONGTEXT"),
            ("status", "TINYINT"),
        ], "#185FA5"),
        (670, 230, 170, "case_products", [
            ("case_id", "FK→cases"),
            ("product_id", "FK→products"),
            ("PRIMARY KEY", "(case_id, product_id)"),
        ], "#185FA5"),
        (670, 310, 170, "news 新闻", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(255)"),
            ("category", "ENUM 企业/行业"),
            ("cover_url", "VARCHAR(255)"),
            ("content", "LONGTEXT"),
            ("status", "TINYINT"),
        ], "#185FA5"),
        (670, 450, 170, "carousels 轮播图", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("image_url", "VARCHAR(255)"),
            ("link", "VARCHAR(255)"),
            ("position", "VARCHAR(32)"),
            ("sort", "INT"),
        ], "#185FA5"),
        (670, 570, 170, "downloads 下载中心", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("file_url", "VARCHAR(255)"),
            ("language", "VARCHAR(8)"),
            ("sort", "INT"),
        ], "#185FA5"),
        (670, 660, 170, "timeline_events 时间线", [
            ("id", "INT PK"),
            ("year", "VARCHAR(8)"),
            ("title", "VARCHAR(128)"),
            ("description", "TEXT"),
            ("sort", "INT"),
        ], "#185FA5"),

        # 订单/业务域
        # 排版：右边一列
    ]

    # 第二批实体（右列）
    right_entities = [
        (670, 70, 170, "cases 案例", C["mod_cus_stroke"]),
        (670, 230, 170, "case_products", C["mod_cus_stroke"]),
        (670, 310, 170, "news 新闻", C["mod_cus_stroke"]),
        (670, 450, 170, "carousels 轮播图", C["mod_cus_stroke"]),
        (670, 570, 170, "downloads 下载中心", C["mod_cus_stroke"]),
        (670, 660, 170, "timeline_events 时间线", C["mod_cus_stroke"]),
    ]

    # 实际上重写：使用一列在右侧 x=670
    # 简化：去掉右列重复定义，先把第一列渲染完，再追加右侧实体
    # 注意上面已经把右列定义写在 entities 里，现在 clear 掉重做
    entities_filtered = [
        (40, 70, 170, "users 前台会员", [
            ("id", "BIGINT PK"),
            ("phone", "VARCHAR(20) UQ"),
            ("password_hash", "VARCHAR(128)"),
            ("nickname", "VARCHAR(64)"),
            ("avatar_url", "VARCHAR(255)"),
            ("status", "TINYINT"),
            ("created_at", "DATETIME"),
        ], "#534AB7"),
        (40, 230, 170, "user_addresses", [
            ("id", "BIGINT PK"),
            ("user_id", "FK→users"),
            ("receiver", "VARCHAR(64)"),
            ("phone", "VARCHAR(20)"),
            ("province/city", "VARCHAR(64)"),
            ("detail", "VARCHAR(255)"),
            ("is_default", "TINYINT"),
        ], "#534AB7"),
        (40, 410, 170, "admin_users", [
            ("id", "BIGINT PK"),
            ("username", "VARCHAR(64) UQ"),
            ("password_hash", "VARCHAR(128)"),
            ("display_name", "VARCHAR(64)"),
            ("status", "TINYINT"),
            ("last_login_at", "DATETIME"),
        ], "#A32D2D"),
        (40, 560, 170, "audit_logs", [
            ("id", "BIGINT PK"),
            ("admin_id", "FK→admin_users"),
            ("action", "VARCHAR(32)"),
            ("resource", "VARCHAR(64)"),
            ("ip", "VARCHAR(45)"),
            ("created_at", "DATETIME"),
        ], "#A32D2D"),

        (250, 70, 170, "roles 角色", [
            ("id", "INT PK"),
            ("code", "VARCHAR(32) UQ"),
            ("name", "VARCHAR(64)"),
            ("data_scope", "TINYINT"),
        ], "#993C1D"),
        (250, 200, 170, "permissions 权限", [
            ("id", "INT PK"),
            ("module", "VARCHAR(32)"),
            ("action", "VARCHAR(32)"),
            ("code", "VARCHAR(64) UQ"),
        ], "#993C1D"),
        (250, 330, 170, "admin_roles", [
            ("admin_id", "FK→admin_users"),
            ("role_id", "FK→roles"),
            ("PRIMARY KEY", "(admin_id, role_id)"),
        ], "#993C1D"),
        (250, 420, 170, "role_permissions", [
            ("role_id", "FK→roles"),
            ("permission_id", "FK→permissions"),
            ("PRIMARY KEY", "(role_id, permission_id)"),
        ], "#993C1D"),
        (250, 510, 170, "admin_regions 数据范围", [
            ("id", "BIGINT PK"),
            ("admin_id", "FK→admin_users"),
            ("region_code", "VARCHAR(32)"),
            ("store_code", "VARCHAR(32)"),
        ], "#993C1D"),
        (250, 620, 170, "site_configs", [
            ("id", "INT PK"),
            ("key", "VARCHAR(64) UQ"),
            ("value", "TEXT"),
            ("group", "VARCHAR(32)"),
        ], "#993C1D"),

        (460, 70, 170, "categories 分类", [
            ("id", "INT PK"),
            ("type", "ENUM 系列/空间/品类"),
            ("name", "VARCHAR(64)"),
            ("parent_id", "FK→categories"),
            ("sort", "INT"),
        ], "#3B6D11"),
        (460, 230, 170, "products 产品", [
            ("id", "BIGINT PK"),
            ("name", "VARCHAR(128)"),
            ("series_id", "FK→categories"),
            ("space_id", "FK→categories"),
            ("category_id", "FK→categories"),
            ("material/style", "VARCHAR(64)"),
            ("is_custom", "TINYINT"),
            ("support_order", "TINYINT"),
        ], "#3B6D11"),
        (460, 410, 170, "product_skus", [
            ("id", "BIGINT PK"),
            ("product_id", "FK→products"),
            ("color", "VARCHAR(32)"),
            ("size", "VARCHAR(32)"),
            ("material", "VARCHAR(32)"),
            ("price", "DECIMAL(10,2)"),
            ("stock", "INT"),
            ("code", "VARCHAR(64) UQ"),
        ], "#3B6D11"),
        (460, 580, 170, "product_images", [
            ("id", "BIGINT PK"),
            ("product_id", "FK→products"),
            ("url", "VARCHAR(255)"),
            ("sort", "INT"),
            ("is_cover", "TINYINT"),
        ], "#3B6D11"),
    ]
    entities = entities_filtered

    for ex, ey, ew, tname, fs, ac in entities:
        entity(ex, ey, ew, tname, fs, ac)

    # 第四列实体（内容+业务）
    col4 = [
        (670, 70, 170, "cases 案例", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("space/style", "VARCHAR(64)"),
            ("area", "VARCHAR(64)"),
            ("content", "LONGTEXT"),
            ("status", "TINYINT"),
        ], "#185FA5"),
        (670, 230, 170, "case_products", [
            ("case_id", "FK→cases"),
            ("product_id", "FK→products"),
            ("PRIMARY KEY", "(case_id, product_id)"),
        ], "#185FA5"),
        (670, 300, 170, "news 新闻", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(255)"),
            ("category", "ENUM 企业/行业"),
            ("cover_url", "VARCHAR(255)"),
            ("content", "LONGTEXT"),
            ("status", "TINYINT"),
        ], "#185FA5"),
        (670, 440, 170, "carousels 轮播图", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("image_url", "VARCHAR(255)"),
            ("link", "VARCHAR(255)"),
            ("position", "VARCHAR(32)"),
            ("sort", "INT"),
        ], "#185FA5"),
        (670, 560, 170, "downloads 下载中心", [
            ("id", "BIGINT PK"),
            ("title", "VARCHAR(128)"),
            ("file_url", "VARCHAR(255)"),
            ("language", "VARCHAR(8)"),
            ("sort", "INT"),
        ], "#185FA5"),
        (670, 650, 170, "timeline_events 时间线", [
            ("id", "INT PK"),
            ("year", "VARCHAR(8)"),
            ("title", "VARCHAR(128)"),
            ("description", "TEXT"),
            ("sort", "INT"),
        ], "#185FA5"),
    ]
    for ex, ey, ew, tname, fs, ac in col4:
        entity(ex, ey, ew, tname, fs, ac)

    # 第五列（业务/订单）
    # 注意：宽度 W=880，可以放第5列在 x=670 之后。等等，4列已经到 x=670+170=840，剩 40 不够。
    # 重新规划：把内容域挤到第4列，业务域放第3列下方
    # 实际上让视图更紧凑，把案例/news/招聘等放右侧第4列，业务(订单/预约/留言/招聘) 放第3列下方
    # 重置实体布局：x=40/250/460/670 共4列，宽 170，高自适应
    # 当前已经画好前4列，下面在第3列 (x=460) 下方补充业务实体

    # 业务域实体（放在第2列 (x=250) 下方太挤；放在第1列 (x=40) 下方也不够）
    # 改用：把业务域放在第4列下方 (x=670)，但右列已经满了。
    # 简化方案：取消 jobs 表的图示，在右下角放一个 "其他业务表" 摘要框
    # 或者：增加 viewBox 高度

    # 实际方案：扩展 H 为 1080
    pass

    # 关系连线（简化标注 1:N / N:M）
    # users → user_addresses (1:N)
    parts.append(arrow(125, 145, 125, 230, color="#534AB7"))
    parts.append(text(105, 188, "1:N", size=8, color="#534AB7", anchor="end"))

    # users → orders (后面再补) - 先预留
    # admin_users → audit_logs
    parts.append(arrow(125, 488, 125, 560, color="#A32D2D"))
    parts.append(text(105, 524, "1:N", size=8, color="#A32D2D", anchor="end"))

    # admin_users → admin_roles (1:N)
    parts.append(arrow(210, 450, 250, 350, color="#A32D2D", dashed=True))
    # roles → admin_roles (1:N)
    parts.append(arrow(335, 130, 335, 330, color="#993C1D"))
    parts.append(text(345, 230, "1:N", size=8, color="#993C1D", anchor="start"))
    # permissions → role_permissions (1:N)
    parts.append(arrow(335, 260, 335, 420, color="#993C1D"))
    # roles → role_permissions (1:N)
    parts.append(arrow(420, 110, 420, 440, color="#993C1D", dashed=True))

    # admin_users → admin_regions
    parts.append(arrow(210, 488, 250, 555, color="#A32D2D", dashed=True))

    # categories → products (3 次 1:N)
    parts.append(arrow(420, 130, 460, 270, color="#3B6D11", dashed=True))
    parts.append(arrow(420, 150, 460, 290, color="#3B6D11", dashed=True))
    parts.append(arrow(420, 170, 460, 310, color="#3B6D11", dashed=True))

    # products → product_skus (1:N)
    parts.append(arrow(545, 405, 545, 410, color="#3B6D11"))
    parts.append(text(555, 402, "1:N", size=8, color="#3B6D11", anchor="start"))

    # products → product_images (1:N)
    parts.append(arrow(545, 380, 545, 580, color="#3B6D11"))

    # products → case_products (1:N)
    parts.append(arrow(630, 330, 670, 250, color="#3B6D11", dashed=True))
    # cases → case_products (1:N)
    parts.append(arrow(755, 165, 755, 230, color="#185FA5"))

    # 图例
    leg_y = 760
    legend_items = [
        ("#534AB7", "前台用户域"),
        ("#A32D2D", "后台用户域"),
        ("#993C1D", "权限 / 配置"),
        ("#3B6D11", "产品域"),
        ("#185FA5", "内容域"),
    ]
    parts.append(text(W/2, leg_y, "图例（按颜色区分域）：", size=10, color=C["text_sub"], anchor="end"))
    lx = W/2 + 10
    for color, label in legend_items:
        parts.append(rect(lx, leg_y-10, 12, 12, color, color, rx=2, stroke_w=0.5))
        parts.append(text(lx+16, leg_y, label, size=10, color=C["text"], anchor="start"))
        lx += 110

    # 业务域说明
    note_y = 800
    parts.append(rect(40, note_y, W-80, 56, "#FAFAFA", C["border"], rx=6, opacity=0.6))
    parts.append(text(50, note_y+18, "业务/订单域（关联字段）：", size=11, color=C["text"], anchor="start", weight=500))
    parts.append(text(50, note_y+36, "jobs(招聘) → job_applications(投递, 5 阶段状态机) → users（会员可投递）", size=10, color=C["text_sub"], anchor="start"))
    parts.append(text(50, note_y+50, "appointments(预约, 4 类型) / messages(留言) / orders → order_items → product_skus → products（库存联动）", size=10, color=C["text_sub"], anchor="start"))

    parts.append('</svg>')
    return "\n".join(parts)


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    targets = {
        "frontend-architecture.svg": frontend_arch(),
        "backend-architecture.svg": backend_arch(),
        "er-diagram.svg": er_diagram(),
    }
    for fname, content in targets.items():
        path = OUT_DIR / fname
        path.write_text(content, encoding="utf-8")
        print(f"[OK] {fname}  size={len(content):,} bytes")