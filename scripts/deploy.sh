#!/usr/bin/env bash
# =============================================================
# YD 家具 — Docker 一键部署脚本（Windows Git Bash / WSL / Linux/macOS）
# 用法：
#   ./scripts/deploy.sh            # 构建 + 启动
#   ./scripts/deploy.sh up         # 同默认
#   ./scripts/deploy.sh down       # 停止
#   ./scripts/deploy.sh logs       # 查看日志
#   ./scripts/deploy.sh reset      # 清空数据重建（谨慎！）
# =============================================================
set -e
cd "$(dirname "$0")/../docker"

CMD="${1:-up}"

case "$CMD" in
  up)
    echo "▶ 构建并启动 YD 全套环境（6 服务）..."
    docker compose build
    docker compose up -d
    echo
    echo "✅ 启动完成！"
    echo "   前台官网：  http://localhost:8080"
    echo "   后台管理：  http://localhost:8080/admin/"
    echo "   API 文档：  http://localhost:8080/api/v1/docs"
    echo "   直连后端：  http://localhost:8000"
    echo "   MySQL：     localhost:3306 (yd/yd_secret_2026)"
    echo "   Redis：     localhost:6379"
    echo
    echo "   演示账号：后台 admin/admin123；会员 13800138001/member123"
    ;;
  down)
    docker compose down
    echo "✅ 已停止"
    ;;
  logs)
    shift || true
    docker compose logs -f "$@"
    ;;
  reset)
    echo "⚠️  将删除全部数据卷（mysql/redis/uploads），不可恢复！"
    read -r -p "确认输入 YES 继续：" ans
    if [ "$ans" = "YES" ]; then
      docker compose down -v
      docker compose up -d --build
      echo "✅ 已重置并重启"
    else
      echo "已取消"
    fi
    ;;
  *)
    echo "用法: $0 [up|down|logs|reset]"
    ;;
esac
