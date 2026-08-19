# 前台 Dockerfile — 多阶段：pnpm install + pnpm build + nginx
# 使用 managed Node 22.22.2 镜像

# ===== Stage 1: build =====
FROM node:22-alpine AS build

WORKDIR /app

# 装 pnpm（用 corepack）
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable && corepack prepare pnpm@latest --activate

# 拷贝 manifests 优先（利用缓存）
COPY yd-frontend/package.json yd-frontend/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

# 拷贝源码 + 构建
COPY yd-frontend ./
RUN pnpm build

# ===== Stage 2: runtime =====
FROM nginx:1.27-alpine

# 拷构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx 静态站点配置
COPY docker/nginx/frontend-default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
