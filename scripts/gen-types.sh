#!/usr/bin/env bash
# 自动生成 TypeScript 类型（ADR-007：Pydantic → TS）
# 从 FastAPI 的 /openapi.json 拉取，生成到 shared/ts-types/
set -e

OUT_DIR="shared/ts-types"
mkdir -p "$OUT_DIR"

echo "==> 拉取 OpenAPI schema"
curl -fsSL http://localhost:8000/openapi.json -o "$OUT_DIR/openapi.json"

echo "==> 用 openapi-typescript 生成 TS 类型"
npx -y openapi-typescript "$OUT_DIR/openapi.json" \
  --output "$OUT_DIR/api-types.ts"

echo "✅ TypeScript 类型已生成 → $OUT_DIR/api-types.ts"
echo "   前端/后台 import 即可：import type { PublicProduct } from '@yd-types/api-types'"
