# YD 家居 — 官网 + 后台管理系统

> **单仓库 monorepo**（基于已确认的项目开发实施方案 v1.0）

YD 家居企业官网与后台管理系统的生产级 Web 应用，对齐 14 个高保真原型与 4 份设计文档。

## 技术栈

| 层 | 技术 | 版本 |
|---|---|---|
| 前台 | Vite + React 19 + TS + Tailwind CSS 3.4 | frontend/ |
| 后台 | Vite + React 19 + TS + Ant Design 5 | admin/ |
| 后端 | FastAPI + SQLAlchemy 2.0 + Pydantic + JWT | backend/ |
| 数据库 | MySQL 8.0（34 张表，见 `数据库设计文档_install_all.sql`） | mysql:8.0 |
| 缓存 | Redis 7（验证码/限流/会话） | redis:7-alpine |
| 反代 | Nginx 1.27 | nginx:1.27-alpine |
| 包管理 | uv（后端）+ pnpm（前端） | uv 0.12 / pnpm 11 |

## 快速启动（Docker Compose 一键）

> ⚠️ **前置**：本机已装 Docker Desktop。  
> 若未装：`https://www.docker.com/products/docker-desktop/`（约 600MB）

```bash
# 一、启动（首次会自动构建并初始化数据库）
docker compose -f docker/docker-compose.yml up -d --build

# 二、等待 MySQL 初始化（约 30-60 秒）
docker compose logs -f mysql

# 三、验证
curl http://localhost:8080/api/v1/health
```

**访问入口**：

| 入口 | URL |
|---|---|
| 前台 | http://localhost:8080/ |
| 后台 | http://localhost:8080/admin/ |
| API | http://localhost:8080/api/ |
| Swagger | http://localhost:8080/api/docs |
| MySQL | localhost:3306（yd / yd_secret_2026） |
| Redis | localhost:6379 |
| 后端直连 | http://localhost:8000 |
| 前台直连 | http://localhost:5180 |
| 后台直连 | http://localhost:5181 |

## 本地直跑（无 Docker）

```bash
# === 后端 ===
cd yd-backend
cp .env.example .env       # Windows: copy .env.example .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# === 前台（新开终端）===
cd yd-frontend
pnpm install
pnpm dev                    # http://localhost:5180

# === 后台（新开终端）===
cd yd-admin
pnpm install
pnpm dev                    # http://localhost:5181
```

## 文档

| 文档 | 路径 |
|---|---|
| PRD | `../PRD_企业家居官网及后台管理系统.md` |
| UI/UX 设计规格 | `../UI文档/UI-UX设计规格文档.md` |
| 开发技术文档 | `../开发文档/开发技术文档.md` |
| 数据库设计文档 | `../开发文档/数据库设计文档.md` |
| 项目开发实施方案 | `../开发文档/项目开发实施方案.md` |
| 默认账号 | `admin / admin123`（首次登录后必须改密码） |

## 当前进度

- ✅ **M0 基础设施**（当前）
  - monorepo 骨架 + Docker Compose 6 容器编排 + Nginx 反代 + 脚本工具
  - 后端：FastAPI + Config + CORS + /health 端点
  - 前台：React 19 + TS + Tailwind 设计 Token + Home 占位
  - 后台：React 19 + TS + AntD + Login 占位
- ⏳ **M1 后端骨架 + 前台 MVP**（下一步）
- ⏳ **M2 后台 + 前台完整**
- ⏳ **M3 部署与运维**

## 常用命令

```bash
# 查看服务状态
docker compose -f docker/docker-compose.yml ps

# 重新构建
docker compose -f docker/docker-compose.yml build

# 重置数据（⚠️ 删除所有数据）
docker compose -f docker/docker-compose.yml down -v

# 仅看后端日志
docker compose -f docker/docker-compose.yml logs -f backend

# 进入后端容器
docker compose -f docker/docker-compose.yml exec backend bash
```

## 团队约定

- **Git**：Conventional Commits（`feat(product): 新增产品列表筛选`）
- **分支**：`main` / `develop` / `feature/<scope>`
- **代码风格**：`ruff check`（后端） + `eslint`（前端）
- **类型同步**：后端 API 变更后跑 `bash scripts/gen-types.sh` 自动同步 TS 类型
