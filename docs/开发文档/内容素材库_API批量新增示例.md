# 内容素材库 API 批量新增示例

> 配套文件:`api_payload_内容素材库_80条.json`(80 条,可直接作为请求体)
> 目标接口:`POST /api/v1/admin/content-materials/batch`(需后端按契约实现,或改造为已有接口)

---

## 一、接口契约

**POST `/api/v1/admin/content-materials/batch`**(需 JWT,`content.view` 权限)

请求体:`ContentMaterialCreate[]`(数组,最多 100 条/批)

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | ✓ | 标题 |
| content | string | ✓ | 简介 / 正文 |
| category | string | ✓ | `产品中心` / `案例展示` / `新闻资讯` / `人才招聘` |
| image_prompt | string | ✗ | AI 配图提示词 |
| sort | int | ✗ | 排序号(默认 0) |
| status | int | ✗ | 1=已发布(默认 1) |

响应:`{ "code": 0, "data": { "created": 80 }, "message": "ok" }`

---

## 二、Node.js 脚本示例(内置 fetch,Node 18+)

```js
const fs = require('fs')

const BASE = 'http://localhost:8000/api/v1'
const TOKEN = '<登录后获取的 access_token>' // 见下方登录示例

async function login() {
  // 1. 获取验证码(若有)
  const cap = await (await fetch(`${BASE}/auth/captcha`)).json()
  // 2. 登录(dev 验证码可填 ABCD)
  const res = await fetch(`${BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'admin', password: 'admin123',
      captcha_id: cap.data.captcha_id, captcha_code: 'ABCD',
    }),
  })
  const body = await res.json()
  return body.data.access_token
}

async function main() {
  const token = await login()
  const items = JSON.parse(fs.readFileSync('api_payload_内容素材库_80条.json', 'utf8'))

  // 分批提交,每批 20 条
  for (let i = 0; i < items.length; i += 20) {
    const batch = items.slice(i, i + 20)
    const res = await fetch(`${BASE}/admin/content-materials/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(batch),
    })
    const body = await res.json()
    console.log(`第 ${i / 20 + 1} 批(${batch.length} 条): code=${body.code} ${body.message}`)
  }
}
main()

---

## 三、curl 示例(单条)

```bash
# 先登录拿 token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","captcha_id":"<CAPTCHA_ID>","captcha_code":"ABCD"}'

# 批量新增(带 Authorization)
curl -s -X POST http://localhost:8000/api/v1/admin/content-materials/batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  --data @api_payload_内容素材库_80条.json
```

---

## 四、Python 脚本示例

```python
import json, requests

BASE = "http://localhost:8000/api/v1"
items = json.load(open("api_payload_内容素材库_80条.json", encoding="utf-8"))

def login():
    cap = requests.get(f"{BASE}/auth/captcha").json()
    r = requests.post(f"{BASE}/auth/login", json={
        "username": "admin", "password": "admin123",
        "captcha_id": cap["data"]["captcha_id"], "captcha_code": "ABCD",
    })
    return r.json()["data"]["access_token"]

token = login()
for i in range(0, len(items), 20):
    batch = items[i:i + 20]
    r = requests.post(f"{BASE}/admin/content-materials/batch", json=batch,
                      headers={"Authorization": f"Bearer {token}"})
    print(f"第 {i//20+1} 批({len(batch)} 条):", r.json())
```

---

## 五、注意事项

1. **先登录再调用**:所有 admin 接口需要 `Authorization: Bearer <token>`
2. **分类值用中文**:`产品中心` / `案例展示` / `新闻资讯` / `人才招聘`,与素材库 md 一致
3. **80 条保证**:`api_payload` 共 80 条(每栏目 20),导入后可用
   `SELECT category, COUNT(*) FROM yd_content_materials GROUP BY category;` 核对
4. **接口不存在?**:当前后端尚无 `/admin/content-materials/batch`,需要新增该端点(参考字段见契约);
   若后端已有 news/cases/jobs 等业务表,也可按栏目分别映射到对应接口
