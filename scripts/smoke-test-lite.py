"""YD 家居 M1 + M2-1 Lite 端到端冒烟测试。

直接 Python，不走 shell 字符串拼接问题。
"""
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import json

API = "http://127.0.0.1:8000"
TEST_CODE = f"YD-TEST-{int(time.time())}"  # 每次跑测试用唯一产品码
TEST_NEWS = f"M2-News-{int(time.time())}"  # 每次跑测试用唯一资讯标题


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

# ===== 9. Public cases (3 个 M2-2 种子) =====
section("9. 案例列表（3 个 M2-2 种子）")
data, code = http("GET", "/api/v1/public/cases")
print(f"  Response: {json.dumps(data, ensure_ascii=False)[:300]}...")
check("GET /public/cases → 200", code == 200)
check("items 非空", len(data.get("data", {}).get("items", [])) == 3)
check("total == 3 (M2-2 种子)", data.get("data", {}).get("total") == 3)

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

# ==========================================================
# M2-1 资讯 + 招聘
# ==========================================================

# 先重新登录（M1 测试已 logout）
section("M2-1.1 重新登录拿 token")
captcha_resp, _ = http("GET", "/api/v1/auth/captcha")
cid = captcha_resp["data"]["captcha_id"]
login_data, code = http("POST", "/api/v1/auth/login", {
    "username": "admin", "password": "admin123",
    "captcha_id": cid, "captcha_code": "ABCD",
})
check("/auth/login → 200", code == 200)
check("code == 0", login_data.get("code") == 0)
token = login_data["data"]["access_token"]

# ===== M2-1.2 Public news list =====
section("M2-1.2 前台资讯列表（4 已发布 + 1 草稿）")
data, code = http("GET", "/api/v1/public/news")
print(f"  total={data.get('data', {}).get('total')}, items={len(data.get('data', {}).get('items', []))}")
check("/public/news → 200", code == 200)
check("total == 4 (草稿不显示)", data.get("data", {}).get("total") == 4)
check("items 数 == 4", len(data.get("data", {}).get("items", [])) == 4)
check("置顶优先", data["data"]["items"][0]["is_top"] == True)

# ===== M2-1.3 Public news category filter =====
section("M2-1.3 资讯分类筛选 company")
data, code = http("GET", "/api/v1/public/news?category=company")
check("/public/news?category=company → 200", code == 200)
check("company 分类 2 条已发布", data.get("data", {}).get("total") == 2)

# ===== M2-1.4 Public news detail =====
section("M2-1.4 资讯详情")
data, code = http("GET", "/api/v1/public/news/1")
check("/public/news/1 → 200", code == 200)
check("返回 title", data["data"]["title"])
check("返回 content", data["data"]["content"])
check("is_published=True", data["data"]["is_published"] == True)

# 浏览量 +1
data2, _ = http("GET", "/api/v1/public/news/1")
check("view_count 自增", data2["data"]["view_count"] == data["data"]["view_count"] + 1)

# ===== M2-1.5 Admin news list =====
section("M2-1.5 后台资讯列表（含草稿）")
data, code = http("GET", "/api/v1/admin/news", token=token)
check("/admin/news → 200", code == 200)
check("total == 5 (含草稿)", data.get("data", {}).get("total") == 5)

# ===== M2-1.6 Admin news CRUD =====
section("M2-1.6 后台创建资讯")
data, code = http("POST", "/api/v1/admin/news", {
    "title": TEST_NEWS,
    "subtitle": "M2-1 测试",
    "category": "company",
    "summary": "Lite 验证用",
    "content": "<p>正文内容</p>",
    "is_published": True,
    "is_top": False,
}, token=token)
check("POST /admin/news → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("返回 id", data["data"]["id"] > 0)
new_news_id = data["data"]["id"]

section("M2-1.7 后台更新资讯")
data, code = http("PUT", f"/api/v1/admin/news/{new_news_id}", {
    "title": TEST_NEWS + " (updated)",
    "subtitle": "更新后",
    "category": "industry",
    "content": "<p>更新正文</p>",
    "is_published": True,
    "is_top": True,
    "is_recommend": True,
}, token=token)
check("PUT /admin/news → 200", code == 200)
check("title 已更新", "updated" in data["data"]["title"])
check("is_top 已更新", data["data"]["is_top"] == True)

section("M2-1.8 后台删除资讯")
data, code = http("DELETE", f"/api/v1/admin/news/{new_news_id}", token=token)
check("DELETE /admin/news → 200", code == 200)
data, _ = http("GET", f"/api/v1/public/news/{new_news_id}")
check("删除后前台 404", "404" in str(data.get("code", "")) or data.get("code") == 404)

# ===== M2-1.9 Jobs public list =====
section("M2-1.9 前台岗位列表（3 个）")
data, code = http("GET", "/api/v1/public/jobs")
check("/public/jobs → 200", code == 200)
check("total == 3", data.get("data", {}).get("total") == 3)
job_id = data["data"]["items"][0]["id"]

# ===== M2-1.10 Jobs public detail =====
section("M2-1.10 岗位详情")
data, code = http("GET", f"/api/v1/public/jobs/{job_id}")
check("/public/jobs/{id} → 200", code == 200)
check("title 含设计师或运营", "设计师" in data["data"]["title"] or "运营" in data["data"]["title"])
check("返回 description", data["data"]["description"])

# ===== M2-1.11 Apply job =====
section("M2-1.11 前台投递岗位")
TEST_APPLY_PHONE = f"137{int(time.time()) % 100000000:08d}"  # 每次唯一手机号防重复投递
data, code = http("POST", "/api/v1/public/jobs/apply", {
    "job_id": job_id,
    "name": "李四",
    "phone": TEST_APPLY_PHONE,
    "email": "lisi@example.com",
})
check("POST /public/jobs/apply → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("返回 stage=applied", data["data"]["stage"] == "applied")
apply_id = data["data"]["id"]

# 重复投递应 400
data, code = http("POST", "/api/v1/public/jobs/apply", {
    "job_id": job_id, "name": "李四", "phone": TEST_APPLY_PHONE,
})
check("重复投递 → 400", "400" in str(code) or data.get("code") == 400)
check("错误信息含'重复'", "重复" in str(data.get("message", "")))

# ===== M2-1.12 Admin jobs list =====
section("M2-1.12 后台岗位列表")
data, code = http("GET", "/api/v1/admin/jobs", token=token)
check("/admin/jobs → 200", code == 200)
check("total == 3", data.get("data", {}).get("total") == 3)

# ===== M2-1.13 Admin job CRUD =====
section("M2-1.13 后台创建岗位")
TEST_JOB = f"测试岗位-{int(time.time())}"
data, code = http("POST", "/api/v1/admin/jobs", {
    "title": TEST_JOB,
    "category": "social",
    "department": "测试部",
    "location": "远程",
    "salary_min_cents": 1000000,
    "salary_max_cents": 2000000,
    "headcount": 1,
    "description": "<p>测试岗描述</p>",
    "requirement": "<p>测试要求</p>",
    "is_activate": True,
}, token=token)
check("POST /admin/jobs → 200", code == 200)
new_job_id = data["data"]["id"]

section("M2-1.14 后台更新 + 软删岗位")
data, code = http("PUT", f"/api/v1/admin/jobs/{new_job_id}", {
    "title": TEST_JOB + " (updated)",
    "category": "social",
    "headcount": 2,
}, token=token)
check("PUT /admin/jobs → 200", code == 200)
data, code = http("DELETE", f"/api/v1/admin/jobs/{new_job_id}", token=token)
check("DELETE /admin/jobs → 200", code == 200)

# ===== M2-1.15 Admin applications list =====
section("M2-1.15 后台投递记录列表")
data, code = http("GET", "/api/v1/admin/jobs/applications", token=token)
check("/admin/jobs/applications → 200", code == 200)
check("total >= 1", data.get("data", {}).get("total", 0) >= 1)
apps = data["data"]["items"]
check("包含李四的投递", any(a["name"] == "李四" for a in apps))
check("job_title 字段已 join", apps[0].get("job_title") is not None)

# ==========================================================
# M2-2-A Cases + Departments
# ==========================================================

# ===== M2-2-A.1 Public cases list =====
section("M2-2-A.1 前台案例列表（3 个种子）")
data, code = http("GET", "/api/v1/public/cases")
check("/public/cases → 200", code == 200)
check("total == 3", data.get("data", {}).get("total") == 3)
case_id = data["data"]["items"][0]["id"]

# ===== M2-2-A.2 Public case detail =====
section("M2-2-A.2 案例详情")
data, code = http("GET", f"/api/v1/public/cases/{case_id}")
check("/public/cases/{id} → 200", code == 200)
check("返回 title", data["data"]["title"])
check("返回 style", data["data"]["style"])
check("返回 description", data["data"]["description"])
check("category 字段已 join", data["data"].get("category") is not None)

# 浏览量 +1
data2, _ = http("GET", f"/api/v1/public/cases/{case_id}")
check("view_count 自增", data2["data"]["view_count"] == data["data"]["view_count"] + 1)

# ===== M2-2-A.3 Admin cases list =====
section("M2-2-A.3 后台案例列表")
data, code = http("GET", "/api/v1/admin/cases", token=token)
check("/admin/cases → 200", code == 200)
check("total >= 3 (软删记录 admin 仍可见)", data.get("data", {}).get("total", 0) >= 3)

# ===== M2-2-A.4 Admin case CRUD =====
section("M2-2-A.4 后台创建案例")
TEST_CASE = f"测试案例-{int(time.time())}"
data, code = http("POST", "/api/v1/admin/cases", {
    "title": TEST_CASE,
    "cover_url": "https://images.unsplash.com/photo-test?w=800",
    "style": "测试风格",
    "area": "100㎡",
    "description": "<p>测试描述</p>",
}, token=token)
check("POST /admin/cases → 200", code == 200)
check("code == 0", data.get("code") == 0)
new_case_id = data["data"]["id"]

section("M2-2-A.5 后台更新案例")
data, code = http("PUT", f"/api/v1/admin/cases/{new_case_id}", {
    "title": TEST_CASE + " (updated)",
    "cover_url": "https://images.unsplash.com/photo-test?w=800",
    "description": "<p>更新后描述</p>",
}, token=token)
check("PUT /admin/cases → 200", code == 200)
check("title 已更新", "updated" in data["data"]["title"])

section("M2-2-A.6 后台删除案例")
data, code = http("DELETE", f"/api/v1/admin/cases/{new_case_id}", token=token)
check("DELETE /admin/cases → 200", code == 200)
# admin 全可见：删除后 GET 应 200 + is_deleted=1
data, code = http("GET", f"/api/v1/admin/cases/{new_case_id}", token=token)
check("删除后 admin GET 仍 200", code == 200)
check("is_deleted == 1", data["data"].get("is_deleted") == 1)

# ===== M2-2-A.7 Admin depts tree =====
section("M2-2-A.7 后台部门树")
data, code = http("GET", "/api/v1/admin/depts", token=token)
check("/admin/depts → 200", code == 200)
check("返回树结构", isinstance(data["data"], list))
check("根节点 >= 1", len(data["data"]) >= 1)
# 验证含子节点（任一根节点有 child 即可）
root_with_kids = [d for d in data["data"] if len(d.get("children", [])) > 0]
check("至少一个根有子部门", len(root_with_kids) >= 1)
if root_with_kids:
    check("根节点含 children", "children" in root_with_kids[0])

# ===== M2-2-A.8 Admin dept flat =====
section("M2-2-A.8 后台部门扁平列表")
data, code = http("GET", "/api/v1/admin/depts/flat", token=token)
check("/admin/depts/flat → 200", code == 200)
check("扁平列表为数组", isinstance(data["data"], list))
check("扁平节点数 >= 4", len(data["data"]) >= 4)

# ===== M2-2-A.9 Admin dept CRUD =====
section("M2-2-A.9 后台创建子部门")
TEST_DEPT = f"测试部门-{int(time.time())}"
# 用根部门 id 作 parent
root_id = data["data"][0]["id"]
data, code = http("POST", "/api/v1/admin/depts", {
    "name": TEST_DEPT,
    "code": f"TD{int(time.time()) % 10000}",
    "parent_id": root_id,
    "sort": 99,
}, token=token)
check("POST /admin/depts → 200", code == 200)
check("返回 path 含 parent_id", "," + str(root_id) + "," in data["data"]["path"])
new_dept_id = data["data"]["id"]

section("M2-2-A.10 后台更新部门")
data, code = http("PUT", f"/api/v1/admin/depts/{new_dept_id}", {
    "name": TEST_DEPT + " (updated)",
    "sort": 50,
}, token=token)
check("PUT /admin/depts → 200", code == 200)

section("M2-2-A.11 后台删除部门")
data, code = http("DELETE", f"/api/v1/admin/depts/{new_dept_id}", token=token)
check("DELETE /admin/depts → 200", code == 200)

# ===== M2-2-A.12 删除有子部门的根应失败 =====
section("M2-2-A.12 删除有子部门的根应 400")
# 找根 id（树根的 parent_id 为 None）
data, _ = http("GET", "/api/v1/admin/depts", token=token)
roots_with_kids = [d for d in data["data"] if len(d.get("children", [])) > 0]
if roots_with_kids:
    root_id_with_kids = roots_with_kids[0]["id"]
    data, code = http("DELETE", f"/api/v1/admin/depts/{root_id_with_kids}", token=token)
    check("删除有子部门的根 → 400", "400" in str(code))
    check("错误信息含'子部门'", "子部门" in str(data.get("message", "")))

# ==========================================================
# M2-2-B Member + Message
# ==========================================================

# ===== M2-2-B.1 会员注册 =====
section("M2-2-B.1 前台会员注册")
TEST_PHONE = f"139{int(time.time()) % 100000000:08d}"  # 唯一手机号
data, code = http("POST", "/api/v1/members/register", {
    "phone": TEST_PHONE,
    "password": "member123",
    "nickname": "测试会员",
})
check("POST /members/register → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("返回 phone", data["data"]["phone"] == TEST_PHONE)
check("不返回 password_hash", "password_hash" not in str(data["data"]))

# ===== M2-2-B.2 重复注册 =====
section("M2-2-B.2 重复手机号注册")
data, code = http("POST", "/api/v1/members/register", {
    "phone": TEST_PHONE, "password": "member123",
})
check("重复注册 → 400", "400" in str(code) or data.get("code") == 400)
check("错误信息含'已注册'", "已注册" in str(data.get("message", "")))

# ===== M2-2-B.3 会员登录 =====
section("M2-2-B.3 会员登录")
data, code = http("POST", "/api/v1/members/login", {
    "phone": TEST_PHONE, "password": "member123",
})
check("POST /members/login → 200", code == 200)
check("code == 0", data.get("code") == 0)
check("返回 access_token", data["data"]["access_token"])
member_token = data["data"]["access_token"]

# ===== M2-2-B.4 会员错误密码 =====
section("M2-2-B.4 会员错误密码")
data, code = http("POST", "/api/v1/members/login", {
    "phone": TEST_PHONE, "password": "wrongpassword",
})
check("错误密码 → 400", "400" in str(code) or data.get("code") == 400)

# ===== M2-2-B.5 会员 me =====
section("M2-2-B.5 会员个人信息 me")
data, code = http("GET", "/api/v1/members/me", token=member_token)
check("GET /members/me → 200", code == 200)
check("phone 一致", data["data"]["phone"] == TEST_PHONE)
check("nickname 一致", data["data"]["nickname"] == "测试会员")

# ===== M2-2-B.6 会员 token 拒绝 =====
section("M2-2-B.6 无 token /members/me")
data, code = http("GET", "/api/v1/members/me")
check("无 token → 401", code == 401)

# ===== M2-2-B.7 前台留言 =====
section("M2-2-B.7 前台提交留言")
data, code = http("POST", "/api/v1/members/messages", {
    "name": "留言测试用户",
    "phone": "13800138099",
    "content": "测试留言：想了解胡桃禮餐桌的价格和定制信息。",
})
check("POST /members/messages → 200", code == 200)
check("status == pending", data["data"]["status"] == "pending")
new_msg_id = data["data"]["id"]

# ===== M2-2-B.8 后台留言列表 =====
section("M2-2-B.8 后台留言列表")
data, code = http("GET", "/api/v1/admin/messages", token=token)
check("GET /admin/messages → 200", code == 200)
check("total >= 3 (2 种子 + 1 新)", data.get("data", {}).get("total", 0) >= 3)

# ===== M2-2-B.9 后台回复留言 =====
section("M2-2-B.9 后台回复留言")
data, code = http("POST", f"/api/v1/admin/messages/{new_msg_id}/reply", {
    "reply_content": "您好，胡桃禮餐桌支持定制，详情可联系门店。",
}, token=token)
check("POST /admin/messages/{id}/reply → 200", code == 200)
check("status == replied", data["data"]["status"] == "replied")
check("返回 reply_content", data["data"]["reply_content"])

# ===== M2-2-B.10 后台会员列表 =====
section("M2-2-B.10 后台会员列表")
data, code = http("GET", "/api/v1/admin/members", token=token)
check("GET /admin/members → 200", code == 200)
check("total >= 3 (2 种子 + 1 新)", data.get("data", {}).get("total", 0) >= 3)

# ===== M2-2-B.11 后台启用/禁用会员 =====
section("M2-2-B.11 后台禁用会员")
# 找到测试会员 id
member_id = None
data, _ = http("GET", f"/api/v1/admin/members?keyword={urllib.parse.quote('测试会员')}", token=token)
for m in data.get("data", {}).get("items", []):
    if m["phone"] == TEST_PHONE:
        member_id = m["id"]
        break
check("找到测试会员", member_id is not None)
if member_id:
    data, code = http("PUT", f"/api/v1/admin/members/{member_id}/status", {"is_activate": False}, token=token)
    check("禁用 → 200", code == 200)
    check("is_activate == 0", data["data"]["is_activate"] == 0)
    # 禁用后登录应 403
    data, code = http("POST", "/api/v1/members/login", {
        "phone": TEST_PHONE, "password": "member123",
    })
    check("禁用后登录 → 403", code == 403)
    # 重新启用
    http("PUT", f"/api/v1/admin/members/{member_id}/status", {"is_activate": True}, token=token)

# ===== M2-2-B.12 后台删除留言 =====
section("M2-2-B.12 后台删除留言")
data, code = http("DELETE", f"/api/v1/admin/messages/{new_msg_id}", token=token)
check("DELETE /admin/messages/{id} → 200", code == 200)

# ===== 汇总 =====
print(f"\n\033[1m════════════════════════════════════════════════════════\033[0m")
print(f"\033[1m  \033[32m通过：{PASS}\033[0m   \033[31m失败：{FAIL}\033[0m\033[0m")
print(f"\033[1m════════════════════════════════════════════════════════\033[0m")

if FAIL > 0:
    sys.exit(1)
print("\n\033[32m🎉 M1 Lite 端到端测试全部通过！\033[0m")
