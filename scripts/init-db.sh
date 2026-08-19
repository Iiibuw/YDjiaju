#!/usr/bin/env bash
# 一键初始化 MySQL 数据库：执行 install_all.sql + 种子数据
# 用法（容器内）：docker exec yd-mysql bash /docker-entrypoint-initdb.d/init.sh
# 或本地：bash scripts/init-db.sh（需 mysql client）

set -e

SCHEMA_FILE="${1:-../开发文档/数据库设计文档_install_all.sql}"

if [ ! -f "$SCHEMA_FILE" ]; then
  echo "❌ 找不到 SQL 文件: $SCHEMA_FILE"
  exit 1
fi

echo "==> 执行 SQL: $SCHEMA_FILE"
mysql -h "${MYSQL_HOST:-localhost}" \
      -P "${MYSQL_PORT:-3306}" \
      -u "${MYSQL_USER:-root}" \
      -p"${MYSQL_PASSWORD:-root_secret_2026}" \
      < "$SCHEMA_FILE"

echo "==> 检查表数量"
TABLE_COUNT=$(mysql -h "${MYSQL_HOST:-localhost}" \
      -P "${MYSQL_PORT:-3306}" \
      -u "${MYSQL_USER:-root}" \
      -p"${MYSQL_PASSWORD:-root_secret_2026}" \
      -N -s -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='yd_furniture';")
echo "==> 创建 $TABLE_COUNT 张表"

if [ "$TABLE_COUNT" -lt 30 ]; then
  echo "⚠️  表数量少于 30，请检查 SQL 是否完整执行"
  exit 1
fi

echo "✅ 数据库初始化完成"
