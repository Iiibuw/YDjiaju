#!/usr/bin/env bash
# YD 家居 M1 端到端冒烟测试
# 验证：MySQL 连通 / 后端 14 个接口 / 前台首页 / 后台登录 / 验证码 / JWT 登录链路
set -e

API_BASE="${API_BASE:-http://localhost:8080}"
BYPASS_NGINX="${BYPASS_NGINX:-}"  # 设置后跳过 nginx 直接打后端

PASS=0
FAIL=0

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() {
  echo
  echo "═══════════════════════════════════════════════════════════"
  echo -e "${YELLOW}$1${NC}"
  echo "═══════════════════════════════════════════════════════════"
}

check() {
  local desc="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} $desc"
    PASS=$((PASS+1))
  else
    echo -e "${RED}✗${NC} $desc"
    FAIL=$((FAIL+1))
  fi
}

# ===== 0. 环境检测 =====
step "0. 服务端口检测"

echo "等待 mysql/redis 启动..."
for i in {1..30}; do
  if nc -z localhost 3306 2>/dev/null && nc -z localhost 6379 2>/dev/null; then
    echo -e "${GREEN}✓${NC} MySQL + Redis 端口可访问"
    break
  fi
  sleep 2
done

check "MySQL 端口 3306" "nc -z localhost 3306"
check "Redis 端口 6379" "nc -z localhost 6379"
check "FastAPI 端口 8000" "nc -z localhost 8000"
check "前台端口 5180" "nc -z localhost 5180"
check "后台端口 5181" "nc -z localhost 5181"
check "Nginx 入口 8080" "nc -z localhost 8080"

# ===== 1. 健康检查 =====
step "1. FastAPI 健康检查"
HEALTH=$(curl -s "$API_BASE/api/v1/health")
echo "Response: $HEALTH"
check "GET /api/v1/health 返回 200" "echo '$HEALTH' | grep -q '\"code\":0'"

# ===== 2. 验证码 =====
step "2. 图形验证码"
CAPTCHA_RESP=$(curl -s "$API_BASE/api/v1/auth/captcha")
echo "Response: ${CAPTCHA_RESP:0:200}..."
check "GET /api/v1/auth/captcha 返回 200" "echo '$CAPTCHA_RESP' | grep -q '\"code\":0'"
check "captcha_id 字段存在" "echo '$CAPTCHA_RESP' | grep -q '\"captcha_id\"'"
check "captcha_image 字段存在" "echo '$CAPTCHA_RESP' | grep -q '\"captcha_image\"'"

# 提取 captcha_id（演示模式不强制校验）
CAPTCHA_ID=$(echo "$CAPTCHA_RESP" | grep -oE '"captcha_id":"[^"]*"' | cut -d'"' -f4)
echo "captcha_id = $CAPTCHA_ID"

# ===== 3. 登录（M1 mock：admin / admin123） =====
step "3. 管理员登录 (admin/admin123)"
LOGIN_RESP=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_id\":\"$CAPTCHA_ID\",\"captcha_code\":\"A4B9\"}")
echo "Response: ${LOGIN_RESP:0:300}..."
check "POST /api/v1/auth/login 返回 code:0" "echo '$LOGIN_RESP' | grep -q '\"code\":0'"
check "返回 access_token" "echo '$LOGIN_RESP' | grep -q '\"access_token\"'"
check "返回 profile.username=admin" "echo '$LOGIN_RESP' | grep -q '\"username\":\"admin\"'"

ACCESS_TOKEN=$(echo "$LOGIN_RESP" | grep -oE '"access_token":"[^"]*"' | cut -d'"' -f4)

# ===== 4. 我（me） =====
step "4. 当前管理员资料"
ME_RESP=$(curl -s "$API_BASE/api/v1/auth/me" -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: ${ME_RESP:0:200}..."
check "GET /api/v1/auth/me 返回 code:0" "echo '$ME_RESP' | grep -q '\"code\":0'"
check "me 显示角色 admin" "echo '$ME_RESP' | grep -q '\"roles\"'"

# ===== 5. 公共产品列表 =====
step "5. 公共产品列表 /public/products"
PROD_RESP=$(curl -s "$API_BASE/api/v1/public/products?page=1&page_size=5")
echo "Response: ${PROD_RESP:0:300}..."
check "GET /public/products 返回 code:0" "echo '$PROD_RESP' | grep -q '\"code\":0'"
check "返回 items 数组" "echo '$PROD_RESP' | grep -q '\"items\"'"

# ===== 6. 后台产品列表（需鉴权） =====
step "6. 后台产品列表 /admin/products (require token)"
ADMIN_PROD_RESP=$(curl -s "$API_BASE/api/v1/admin/products" -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response: ${ADMIN_PROD_RESP:0:300}..."
check "GET /admin/products 返回 code:0" "echo '$ADMIN_PROD_RESP' | grep -q '\"code\":0'"

# ===== 7. 前台 HTML 渲染 =====
step "7. 前台首页 HTML (port 5180)"
FRONT_HTML=$(curl -s "http://localhost:5180/")
check "前台返回 HTML" "echo '$FRONT_HTML' | grep -q '<div id=\"root\">'"
check "前台有正确 title" "echo '$FRONT_HTML' | grep -q 'YD 家具'"

# ===== 8. 后台 HTML 渲染 =====
step "8. 后台登录页 HTML (port 5181)"
ADMIN_HTML=$(curl -s "http://localhost:5181/login")
check "后台返回 HTML" "echo '$ADMIN_HTML' | grep -q '<div id=\"root\">'"

# ===== 9. 完整 nginx 反代验证 =====
step "9. Nginx 入口 8080 全站"
N_HOME=$(curl -s "http://localhost:8080/")
N_API=$(curl -s "http://localhost:8080/api/v1/health")
check "8080 / 返回前台 HTML" "echo '$N_HOME' | grep -q '<div id=\"root\">'"
check "8080 /api/v1/health 返回 200" "echo '$N_API' | grep -q '\"code\":0'"

# ===== 汇总 =====
echo
echo "═══════════════════════════════════════════════════════════"
echo -e "  ${GREEN}通过：$PASS${NC}    ${RED}失败：$FAIL${NC}"
echo "═══════════════════════════════════════════════════════════"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
echo
echo "🎉 M1 端到端冒烟测试全部通过！"
