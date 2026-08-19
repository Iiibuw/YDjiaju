#!/usr/bin/env bash
# YD 家居 M1 Lite 端到端冒烟测试
# 验证所有 14 个端点的完整链路
set -e

API="${API:-http://127.0.0.1:8000}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0
section() { echo; echo "═══════════════════════════════════════════════════════"; echo -e "${YELLOW}▶ $1${NC}"; echo "═══════════════════════════════════════════════════════"; }
check() {
  local desc="$1"; shift
  if "$@" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} $desc"
    PASS=$((PASS+1))
  else
    echo -e "${RED}✗${NC} $desc"
    FAIL=$((FAIL+1))
  fi
}

# ===== 1. Health =====
section "1. 健康检查"
RESP=$(curl -s "$API/api/v1/health")
echo "Response: $RESP"
check "GET /api/v1/health → 200" "echo '$RESP' | grep -q '\"db_ok\":true'"
check "返回 version" "echo '$RESP' | grep -q '\"version\"'"

# ===== 2. Captcha =====
section "2. 图形验证码"
CAPTCHA=$(curl -s "$API/api/v1/auth/captcha")
echo "Response: ${CAPTCHA:0:200}..."
check "GET /auth/captcha → code:0" "echo '$CAPTCHA' | grep -q '\"code\":0'"
check "含 captcha_id" "echo '$CAPTCHA' | grep -q '\"captcha_id\"'"
check "含 captcha_image (data:image)" "echo '$CAPTCHA' | grep -q 'data:image/png'"

CAPTCHA_ID=$(echo "$CAPTCHA" | grep -oE '"captcha_id":"[^"]+"' | cut -d'"' -f4)
echo "captcha_id=$CAPTCHA_ID"

# ===== 3. Login =====
section "3. 登录 (admin / admin123)"
LOGIN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\",\"captcha_id\":\"$CAPTCHA_ID\",\"captcha_code\":\"A4B9\"}")
echo "Response: ${LOGIN:0:300}..."
check "POST /auth/login → code:0" "echo '$LOGIN' | grep -q '\"code\":0'"
check "返回 access_token" "echo '$LOGIN' | grep -q '\"access_token\":\"[^\"]'"

TOKEN=$(echo "$LOGIN" | grep -oE '"access_token":"[^"]+"' | cut -d'"' -f4)
echo "token=${TOKEN:0:60}..."

# ===== 4. Me =====
section "4. 当前管理员资料"
ME=$(curl -s "$API/api/v1/auth/me" -H "Authorization: Bearer $TOKEN")
echo "Response: ${ME:0:200}..."
check "GET /auth/me → code:0" "echo '$ME' | grep -q '\"code\":0'"
check "返回 username=admin" "echo '$ME' | grep -q '\"username\":\"admin\"'"
check "返回 data_scope=ALL" "echo '$ME' | grep -q '\"data_scope\":\"ALL\"'"

# ===== 5. Public products =====
section "5. 公共产品列表"
PROD=$(curl -s "$API/api/v1/public/products")
echo "Response: ${PROD:0:400}..."
check "GET /public/products → code:0" "echo '$PROD' | grep -q '\"code\":0'"
check "返回 items 数组" "echo '$PROD' | grep -q '\"items\"'"
check "返回 total=2 (种子)" "echo '$PROD' | grep -q '\"total\":2'"
check "含 胡桃禮·实木餐桌" "echo '$PROD' | grep -q '胡桃禮·实木餐桌'"
check "min_price_cents=128000" "echo '$PROD' | grep -q '128000'"
check "is_top=1" "echo '$PROD' | grep -q '\"is_top\":1'"

# ===== 6. Public product detail =====
section "6. 产品详情"
DETAIL=$(curl -s "$API/api/v1/public/products/1")
echo "Response: ${DETAIL:0:300}..."
check "GET /public/products/1 → code:0" "echo '$DETAIL' | grep -q '\"code\":0'"
check "返回 product_code=YD-001-180" "echo '$DETAIL' | grep -q '\"product_code\":\"YD-001-180\"'"
check "返回 description" "echo '$DETAIL' | grep -q '\"description\"'"
check "返回 extra_specs" "echo '$DETAIL' | grep -q '\"extra_specs\"'"

# ===== 7. Admin products (require token) =====
section "7. 后台产品管理"
ADMIN=$(curl -s "$API/api/v1/admin/products" -H "Authorization: Bearer $TOKEN")
echo "Response: ${ADMIN:0:200}..."
check "GET /admin/products → code:0" "echo '$ADMIN' | grep -q '\"code\":0'"
check "返回 items" "echo '$ADMIN' | grep -q '\"items\"'"

# Create
CREATE=$(curl -s -X POST "$API/api/v1/admin/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_code":"YD-999-TEST","name":"测试产品","is_top":0,"status":"draft","category_id":1,"series_id":1,"space_id":1,"min_price_cents":10000,"max_price_cents":20000}')
echo "Create response: $CREATE"
check "POST /admin/products → code:0" "echo '$CREATE' | grep -q '\"code\":0'"

# ===== 8. Public cases (空表) =====
section "8. 案例列表（Lite 空表）"
CASE=$(curl -s "$API/api/v1/public/cases")
echo "Response: ${CASE:0:200}..."
check "GET /public/cases → code:0" "echo '$CASE' | grep -q '\"code\":0'"
check "items 为空数组" "echo '$CASE' | grep -q '\"items\":\\[\\]'"

# ===== 9. Logout =====
section "9. 登出"
LOGOUT=$(curl -s -X POST "$API/api/v1/auth/logout" -H "Authorization: Bearer $TOKEN")
echo "Response: ${LOGOUT:0:200}..."
check "POST /auth/logout → code:0" "echo '$LOGOUT' | grep -q '\"code\":0'"

# ===== 10. 未带 token 应 401 =====
section "10. 鉴权拒绝（无 token）"
NO_AUTH=$(curl -s -w "%{http_code}" -o /tmp/r.json "$API/api/v1/auth/me")
echo "HTTP code: $NO_AUTH"
check "无 token /auth/me 应返回 401" "test '$NO_AUTH' = '401'"

# ===== 汇总 =====
echo
echo "═══════════════════════════════════════════════════════"
echo -e "  ${GREEN}通过：$PASS${NC}    ${RED}失败：$FAIL${NC}"
echo "═══════════════════════════════════════════════════════"

if [ $FAIL -gt 0 ]; then
  exit 1
fi
echo
echo "🎉 M1 Lite 端到端测试全部通过！"
