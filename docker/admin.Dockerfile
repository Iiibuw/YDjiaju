# 后台 Dockerfile — 同前台，仅 base 路径不同（vite base=/admin/）
FROM node:22-alpine AS build

WORKDIR /app
ENV PNPM_HOME=/pnpm
ENV PATH=$PNPM_HOME:$PATH
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY yd-admin/package.json yd-admin/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile || pnpm install

COPY yd-admin ./
RUN pnpm build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback（含 try_files /index.html）
COPY docker/nginx/frontend-default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -q --spider http://localhost/ || exit 1
CMD ["nginx", "-g", "daemon off;"]
