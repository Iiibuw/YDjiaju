# 后端 Dockerfile — 多阶段：builder + runtime
# 使用 managed Python 3.13.12 镜像

# ===== Stage 1: builder =====
FROM python:3.13-slim AS builder

WORKDIR /app

# 装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 装依赖（利用 Docker 缓存）
COPY yd-backend/pyproject.toml ./
COPY yd-backend/.python-version ./
RUN uv sync --no-install-project --frozen

# 拷源码
COPY yd-backend/app ./app
RUN uv sync --frozen

# ===== Stage 2: runtime =====
FROM python:3.13-slim

WORKDIR /app

# 拷贝 venv 与源码
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app ./app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
