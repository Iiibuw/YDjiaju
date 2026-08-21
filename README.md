# YD 家居 — 官网 + 后台管理系统

> **单仓库 monorepo**（基于已确认的《项目开发实施方案》v1.8，阶段 0–6 全部完成）

YD 家居企业官网（前台展示）+ 后台管理系统，FastAPI 实现（后端）+ 双形态前端：**单文件 HTML 演示版（默认，开箱即用）** 与 **React 工程版（源码，可单独开发）**。对齐 14 个高保真原型与 4 份设计文档（PRD / UI-UX / 数据库设计 / 开发技术文档）。

## 技术栈

| 层 | 技术 | 目录 |
|---|---|---|
| 前台（演示版） | 单文件 HTML + Tailwind CDN + Hash 路由（零依赖） | `web_前台_YD家具.html` |
| 后台（演示版） | 单文件 HTML + Tailwind CDN（11 模块真实 CRUD） | `web_后台_YD家具.html` |
| 前台（React 工程） | Vite + React 19 + TS + Tailwind 3.4 + Router 7 + Zustand | `yd-frontend/` |
| 后台（React 工程） | Vite + React 19 + TS + Ant Design 5 | `yd-admin/` |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic + python-jose + bcrypt | `yd-backend/` |
| 数据库 | MySQL 8.0（34 张表）**或** SQLite（Lite 模式，零依赖） | `yd-backend/yd_lite.db` |
| 缓存 | Redis 7（可选；Lite 模式跳过，验证码走内存 mock） | — |
| 演示服务器 | `scripts/ydf_demo_server.py`（静态文件 + `/api` 同源代理 → :8000） | — |

> ⚠️ **无 Docker 约束**（开发技术文档 v1.1.1）：本仓库不含 Dockerfile / docker-compose，本地优先 **Lite 模式（SQLite）**，一键启动。

## 快速启动（Windows 双击）

```bat
run-dev.bat
```

脚本（`scripts/dev-windows.ps1`）自动：初始化 SQLite 数据库（34 表 + 种子）→ 启动后端（:8000）→ 启动演示服务器（:5280，托管前台/后台 + API 同源代理）。

> 需要本机 MySQL 时：`run-dev.bat -MySQL`（先按 `.env.mysql.example` 配置凭据）。

## 访问入口（一个端口全通）

| 入口 | URL |
|---|---|
| **统一入口页**（推荐） | http://localhost:5280/ |
| 前台官网 | http://localhost:5280/web_前台_YD家具.html |
| 后台管理 | http://localhost:5280/web_后台_YD家具.html |
| API 文档（Swagger） | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/api/v1/health |

> 演示服务器把 `/api/*` 反向代理到后端 :8000，**页面与接口同源**，浏览器无跨域问题，前后端数据实时互通（后台增删改 → 前台刷新即同步）。

## 账号

| 角色 | 账号 | 密码 | 权限 |
|---|---|---|---|
| 超级管理员 | `admin` | `admin123` | 全部 11 模块（仪表盘/轮播/产品/案例/新闻/招聘/关于/预约/留言/订单/系统） |
| 内容编辑 | `editor` | `admin123` | 内容域模块 |
| 产品管理员 | `product` | `admin123` | 产品/轮播/订单查看 |
| 客服主管 | `service` | `admin123` | 预约/留言/订单查看 |
| 订单专员 | `order` | `admin123` | 订单/预约 |

前台会员：注册手机号即用（种子演示：`13800138001 / member123`）。

> 后台登录需图形验证码；Dev 模式（DEBUG=true）下验证码填 `ABCD` 即过。

## 手动启动（三端分离）

```bash
# 1. 后端（SQLite 零依赖；数据文件 yd-backend/yd_lite.db）
cd yd-backend
uv sync && uv run scripts/init_lite.py        # 首次：建表 + 种子（幂等）
uv run uvicorn app.main:app --port 8000

# 2. 演示服务器（前台/后台单文件 + /api 代理；仓库根目录运行）
cd ..
uv run python scripts/ydf_demo_server.py --port 5280 --api http://127.0.0.1:8000 --dir .
# 浏览器打开 http://localhost:5280/

# 3. （可选）React 源码前端单独开发调试
cd yd-frontend && pnpm install && pnpm dev    # http://localhost:5180
cd yd-admin   && pnpm install && pnpm dev     # http://localhost:5181
```

## 测试与质量门禁

```bash
# 后端：22 个端到端用例（RBAC / 内容域 / 系统域 / public / 会员闭环）
cd yd-backend && .venv/Scripts/python.exe -m pytest tests/ -v

# React 前端：类型检查 + 生产构建
cd yd-frontend && pnpm typecheck && pnpm build
cd yd-admin   && pnpm typecheck && pnpm build
```

已覆盖：鉴权（JWT/验证码/防爆破）、RBAC 权限点拦截、内容域/系统域 CRUD、前台 public 接口、会员注册登录下单投递闭环。

## 功能清单（阶段 0–6 已交付）

- **后台**（真实 CRUD 全模块、47 个权限点、5 类角色）：
  - 仪表盘统计（6 项计数 + 7 日趋势）｜ 轮播图 ｜ 分类（树形） ｜ 产品 ｜ 案例 ｜ 新闻 ｜ 招聘+投递 ｜ 关于我们（区块/图集） ｜ 下载中心 ｜ 站点配置 ｜ 客服关键词 ｜ 预约（状态流转） ｜ 留言（回复） ｜ 订单（状态流转） ｜ 会员 ｜ 部门 ｜ 系统管理（角色/权限/管理员）
- **前台**（多页面 SPA，数据驱动）：
  - 首页（真实轮播/推荐产品）｜ 产品中心（三维筛选/搜索/分页/加购） ｜ 案例 ｜ 新闻 ｜ 招聘（投递） ｜ 关于我们 ｜ 下载中心 ｜ 购物车（下单闭环） ｜ 会员登录/注册 ｜ 搜索/客服/预约浮窗

## 目录结构

```
yd-furniture/
├── web_前台_YD家具.html        # 前台演示版（单文件 SPA）
├── web_后台_YD家具.html        # 后台演示版（单文件，11 模块真实 CRUD）
├── index.html                  # 统一入口页（三入口 + 后端实时状态）
├── yd-backend/          # FastAPI：app/{api,core,db,models,schemas,services}
│   ├── scripts/init_lite.py    # SQLite 建表 + 种子
│   └── tests/                  # pytest 22 用例
├── yd-frontend/         # 前台 React（Vite + Tailwind + Router 7 + Zustand）
├── yd-admin/            # 后台 React（Ant Design）
├── scripts/dev-windows.ps1     # 一键启动（后端 + 演示服务器）
├── scripts/ydf_demo_server.py  # 演示服务器（静态 + /api 反向代理）
├── run-dev.bat          # Windows 双击入口
└── M3_Lite运行指南.md   # Lite 模式详细说明
```

## 数据库

- 34 张表，以 SQLAlchemy 模型为 DDL 唯一真相源（`yd-backend/app/models/`），MySQL/SQLite 双 dialect 兼容。
- 关键约束：`chk_products_draft_no_top`、`chk_orders_amount`、`chk_products_category_or_space`、`chk_categories_no_self_parent` 等。
- 价格一律整数分（`*_cents`）；软删除 `deleted_at/is_deleted`；数据范围 4 级 `ALL/REGION/STORE/SELF`（白名单表：orders/appointments/messages/job_applications）。
- 完整字段定义见 `../开发文档/数据库设计文档.md`。

## 已知债务（后续迭代）

- 支付（payments）为占位（线下/对公打款）；`product_skus` 未接入产品（价格用主表区间兜底）。
- 验证码/登录防爆破为进程内存存储（多实例需 Redis）。
- M2 内容模块写操作未接审计日志（系统管理已接入示范）。
- React 工程前端（yd-frontend/yd-admin）与演示版功能并行，日常演示/验收请用 5280 演示入口；React 版用于正式工程演进。
