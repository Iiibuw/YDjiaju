"""YD 家居 M1 Lite 端到端冒烟测试。

直接 Python，不走 shell 字符串拼接问题。
"""
import sys
import time
import urllib.error
import urllib.request
import json

API = "http://127.0.0.1:8000"
TEST_CODE = f"YD-TEST-{int(time.time())}"  # 每次跑测试用唯一产品码


def http(method, path, data=None, token=None):
    """极简 HTTP 客户端。错误响应返回 (raw_text, code)。"""
    url = f"{API}{path}"
    headers = {"Content-Type": "application/json"} if data else {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode()
            try:
                return json.loads(raw), resp.status
            except json.JSONDecodeError:
                return {"_raw": raw}, resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return json.loads(raw or "{}"), e.code
        except json.JSONDecodeError:
            return {"_raw": raw, "message": str(e)}, e.code


PASS = 0
FAIL = 0


def check(desc, cond):
    global PASS, FAIL
    if cond:
        print(f"  \033[32m✓\033[0m {desc}")
        PASS += 1
    else:
        print(f"  \033[31m✗\033[0m {desc}")
        FAIL += 1


def section(name):
    print(f"\n\033[1;33m▶ {name}\033[0m")


# ===== 1. Health =====
section("1. 健康检查")
data, code = http("GET", "/api/v1/health")
print(f"  Response: {data}")
check("GET /api/v1/health → 200", code == 200)
check("db_ok=true", data.get("db_ok") is True)
check("返回 service 名", "YD" in str(data.get("service", "")))

# ===== 2. Captcha =====
section("2. 图形验证码")
data, code = http("GET", "/api/v1/auth/captcha")
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
check("GET /auth/captcha → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("含 captcha_id", "captcha_id" in data.get("data", {}))
check("captcha_image 是 PNG base64", "data:image/png;base64" in data.get("data", {}).get("captcha_image", ""))

captcha_id = data["data"]["captcha_id"]

# ===== 3. Login =====
section("3. 登录 (admin / admin123 + dev captcha ABCD)")
data, code = http("POST", "/api/v1/auth/login", {
    "username": "admin",
    "password": "admin123",
    "captcha_id": captcha_id,
    "captcha_code": "ABCD",  # Dev 模式固定码（auth_service 在 DEBUG=True 时接受）
})
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:300]}...")
check("POST /auth/login → 200", code == 200)
check("code == 0", data.get("code") == 0)
token = data.get("data", {}).get("access_token")
check("返回 access_token", bool(token))

# ===== 4. Me =====
section("4. 当前管理员资料")
data, code = http("GET", "/api/v1/auth/me", token=token)
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:300]}...")
check("GET /auth/me → 200", code == 200)
check("username=admin", data.get("data", {}).get("username") == "admin")
check("data_scope=ALL", data.get("data", {}).get("data_scope") == "ALL")
check("id=1", data.get("data", {}).get("id") == 1)

# ===== 5. Public products =====
section("5. 公共产品列表")
data, code = http("GET", "/api/v1/public/products?page=1&page_size=10")
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:400]}...")
check("GET /public/products → 200", code == 200)
items = data.get("data", {}).get("items", [])
check("items 数组非空", len(items) > 0)
check("total == 2 (种子)", data.get("data", {}).get("total") == 2)
check("含 '胡桃禮·实木餐桌'", any("胡桃禮·实木餐桌" in i.get("name", "") for i in items))
check("价格字段 min_price_cents=128000", items[0].get("min_price_cents") == 128000)
check("is_top=1", items[0].get("is_top") == 1)
check("status=on_sale", items[0].get("status") == "on_sale")
check("front-end 友好 price_yuan", "price_yuan" in items[0])

# ===== 6. Product detail =====
section("6. 产品详情 /public/products/1")
data, code = http("GET", "/api/v1/public/products/1")
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:400]}...")
check("GET /public/products/1 → 200", code == 200)
check("product_code=YD-001-180", data.get("data", {}).get("product_code") == "YD-001-180")
check("返回 description", bool(data.get("data", {}).get("description")))
check("返回 extra_specs (dict)", isinstance(data.get("data", {}).get("specs"), dict))
check("规格含 '黑胡桃木'", "黑胡桃木" in str(data.get("data", {}).get("specs", "")))

# ===== 7. Admin products =====
section("7. 后台产品列表 (require token)")
data, code = http("GET", "/api/v1/admin/products", token=token)
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
check("GET /admin/products → 200", code == 200)
check("code == 0", data.get("code") == 0)

# ===== 8. Admin create =====
section("8. 后台创建产品")
data, code = http("POST", "/api/v1/admin/products", {
    "product_code": TEST_CODE,
    "name": "测试产品",
    "subtitle": "Lite 验证用",
    "min_price_cents": 99000,
    "max_price_cents": 99000,
    "status": "draft",
    "category_id": 1,
    "series_id": 1,
    "space_id": 1,
}, token=token)
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:300]}...")
check("POST /admin/products → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("返回产品含 product_code", TEST_CODE in str(data))

# ===== 9. Public cases (空表) =====
section("9. 案例列表（Lite 空表）")
data, code = http("GET", "/api/v1/public/cases")
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
check("GET /public/cases → 200", code == 200)
check("items 为 []", data.get("data", {}).get("items") == [])
check("total == 0", data.get("data", {}).get("total") == 0)

# ===== 10. Logout =====
section("10. 登出")
data, code = http("POST", "/api/v1/auth/logout", token=token)
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
check("POST /auth/logout → 200", code == 200)

# ===== 11. 鉴权拒绝 =====
section("11. 鉴权拒绝（无 token）")
data, code = http("GET", "/api/v1/auth/me")
check("无 token /auth/me → 401", code == 401)
check("错误信息 含'未提供'", "未提供" in str(data.get("message", "")))

data, code = http("GET", "/api/v1/admin/products")
check("无 token /admin/products → 401", code == 401)

# ===== 12. 错误密码（应业务错） =====
section("12. 错误密码登录（密码 ≥ 6 字符）")
captcha_resp, _ = http("GET", "/api/v1/auth/captcha")
cid = captcha_resp["data"]["captcha_id"]
data, code = http("POST", "/api/v1/auth/login", {
    "username": "admin", "password": "wrongpassword",
    "captcha_id": cid, "captcha_code": "ABCD",
})
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:200]}...")
check("业务错应返回 4xx (400 或 422)", "400" in str(code) or "401" in str(code))
check("code != 0 (业务失败)", data.get("code") != 0)
check("错误信息含'账号或密码'", "账号或密码" in str(data.get("message", "")) or "password" in str(data).lower())

# ===== 汇总 =====
print(f"\n\033[1m════════════════════════════════════════════════════════\033[0m")
print(f"\033[1m  \033[32m通过：{PASS}\033[0m   \033[31m失败：{FAIL}\033[0m\033[0m")
print(f"\033[1m════════════════════════════════════════════════════════\033[0m")

if FAIL > 0:
    sys.exit(1)
print("\n\033[32m🎉 M1 Lite 端到端测试全部通过！\033[0m")
