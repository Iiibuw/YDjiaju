# YD 家居后端（FastAPI）

## 启动（Docker Compose 一键启动）

参见仓库根目录 `README.md` 与 `docker/docker-compose.yml`。容器内自动执行 `uv sync` + 启动 uvicorn。

## 本地直跑（开发用）

```bash
# 1. 创建虚拟环境并装依赖
uv sync

# 2. 复制环境变量
cp .env.example .env
# 编辑 .env，把 DB_HOST/REDIS_HOST 改为 localhost（若本地有 MySQL/Redis）

# 3. 启动
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs`（Swagger 自动生成）。

## 目录

```
app/
  main.py            # FastAPI 入口
  core/config.py     # 环境变量
  db/session.py      # SQLAlchemy 引擎
  api/v1/endpoints/  # 路由（health 已就绪）
alembic/             # 数据库迁移（M1 启用）
tests/               # pytest（M1 启用）
```

## 当前状态

- ✅ M0 骨架：FastAPI 启动 + /health 端点 + CORS + Config
- ⏳ M1 待办：Alembic 迁移 + 鉴权 + 业务接口
