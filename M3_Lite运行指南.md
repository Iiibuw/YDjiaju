# YD 家居 — M3 Lite 模式运行指南（无 Docker）

适用于：Docker Hub 拉不动、Windows 非专业版、或想直接在本机跑整套的场景。
**完全不依赖 Docker 镜像**，用你**本机 MySQL 8.0** 直接跑。

## 一、前提
- 本机已安装并**启动 MySQL 8.0**（默认端口 3306）
- 本机已安装 Python（含 `uv`）+ Node.js（含 `npm`，有 `pnpm` 更优）
- 已 `git clone` 并 `cd yd-furniture`

## 二、一键启动（推荐）
双击 `scripts/dev-windows.ps1`（或在 PowerShell 中执行）。

脚本会自动：
1. 生成 `yd-backend/.env.mysql` 并复制为 `.env`（指向 localhost MySQL）
2. **预检 MySQL 连通性**（连不上会提示如何修改并退出）
3. 初始化数据库（建库 `yd_furniture` + 14 张表 + 种子数据）
4. 弹出 3 个窗口：后端 8000 / 前台 5180 / 后台 5181

> 脚本已内置 **pnpm→npm 兜底**：没装 pnpm 会自动改用 npm。

## 三、若你的 MySQL 账号/密码不是默认的 `yd` / `yd_secret_2026`
编辑 `yd-backend/.env.mysql` 第 29–30 行：
```
DB_USER=你的MySQL账号
DB_PASSWORD=你的MySQL密码
```
保存后重新双击 `dev-windows.ps1`（该账号需有**建库权限**）。

## 四、访问地址
| 端 | 地址 |
|----|------|
| 前台 | http://localhost:5180 |
| 后台 | http://localhost:5181 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

账号：
- 后台管理员：`admin` / `admin123`
- 前台会员：`13800138001` / `member123`

## 五、手动分步（排查时用）
```bash
# 1. 后端：初始化 + 启动（MySQL 模式）
cd yd-backend
cp .env.example .env        # 并改 DB_HOST=localhost + 你的账号密码
uv run python scripts/init_lite.py --type=mysql
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. 前台
cd yd-frontend && npm run dev        # → 5180

# 3. 后台
cd yd-admin && npm run dev           # → 5181
```

## 六、常见问题
- **MySQL 连不上**：确认 MySQL80 服务已启动；确认 `.env.mysql` 的账号密码正确且有建库权限。
- **Redis 不需要**：Dev/Lite 模式验证码走内存字典，无需真实 Redis。
- **想用 SQLite 零依赖**：把 `.env` 改成 `DB_TYPE=sqlite`，运行 `uv run python scripts/init_lite.py`（不带 `--type`），同样能起后端。

## 七、已验证
后端启动自建于 ORM 建表 + 幂等种子（与 MySQL 模式共用 `app/db/seed.py`）；
沙箱（Git Bash）中以 SQLite 等价模式完成三端 + 后端 API 全链路冒烟：
admin 登录 → 产品/订单/会员/预约管理；会员登录 → 我的订单/个人中心；
公开产品列表；图形验证码生成。后台 `/admin/` 路径 nginx 配置已在 Docker 版修正。
