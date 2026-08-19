#!/usr/bin/env bash
# 统一代码检查（ruff + eslint + typecheck）
set -e

echo "==> 后端 ruff"
cd yd-backend && uv run ruff check app/ tests/ && cd ..

echo "==> 前台 typecheck"
cd yd-frontend && pnpm typecheck && cd ..

echo "==> 前台 lint"
cd yd-frontend && pnpm lint && cd ..

echo "==> 后台 typecheck"
cd yd-admin && pnpm typecheck && cd ..

echo "==> 后台 lint"
cd yd-admin && pnpm lint && cd ..

echo "✅ 全部通过"
