# YD 家居 — M3 Lite 模式运行指南（无 Docker / 无 MySQL）

技术栈：**前端 React + 后端 FastAPI**。
本指南适用于：Docker 已卸载、Docker Hub 拉不动、或想直接在本机零依赖跑整套的场景。

> **默认 SQLite 零依赖**：不需要 Docker、不需要任何 MySQL/Redis。
> 双击脚本即用，数据库是一个本地文件 `yd-backend/yd_lite.db`。
> 只有当你**本机另外装了 MySQL 8.0** 时，才用 `run-dev.bat -MySQL` 切换。

## 一、前提
- 本机已安装 Python（含 `uv`）+ Node.js（含 `npm`，有 `pnpm` 更优）
- 已 `git clone` 并 `cd yd-furniture`

## 二、一键启动（推荐，SQLite 零依赖）
**双击 `run-dev.bat`**（项目根目录 `yd-furniture\run-dev.bat`）。

脚本会自动：
1. 生成 `yd-backend/.env.sqlite` 并复制为 `.env`（指向本地 SQLite 文件）
2. 初始化数据库（建 14 张表 + 种子数据，首次约几秒）
3. 弹出 3 个窗口：后端/FastAPI 8000 / 前台/React 5180 / 后台/React 5181

> 脚本已内置 **pnpm→npm 兜底**：没装 pnpm 会自动改用 npm。
> 若提示找不到 `uv`/`node`，说明它们没进 PATH，脚本会让 PowerShell 补常用路径；仍不行就重装并把它们加入 PATH。

## 三、访问地址
| 端 | 地址 |
|----|------|
| 前台（React） | http://localhost:5180 |
| 后台（React，base `/admin/`） | http://localhost:5181/admin/ |
| 后端（FastAPI） | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

账号：
- 后台管理员：`admin` / `admin123`
- 前台会员：`13800138001` / `member123`

## 四、可选：本机有 MySQL 8.0 时切换
如果你后来在本机装了 MySQL 8.0，想用它而不是 SQLite：
```cmd
run-dev.bat -MySQL
```
脚本会改用 `yd-backend/.env.mysql`（默认账号 `Iiibuw` / 你的密码），预检连通性后初始化 `yd_furniture` 库。
账号密码不符时编辑 `yd-backend/.env.mysql` 的 `DB_USER`/`DB_PASSWORD` 再重跑。

## 五、手动分步（排查时用）
```bash
# SQLite 模式（默认，零依赖）
cd yd-backend
uv run python scripts/init_lite.py          # 建表+种子
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前台 / 后台（另开两个终端）
cd yd-frontend && npm run dev -- --port 5180 --host 127.0.0.1   # → 5180
cd yd-admin    && npm run dev -- --port 5181 --host 127.0.0.1   # → 5181
```

## 六、常见问题
- **双击 `.ps1` 用记事本打开 / 报执行策略错**：不要直接双击 `.ps1`，改双击 `run-dev.bat`（它已用 `ExecutionPolicy Bypass` 包装）。
- **中文/emoji 报错 `Unexpected token`**：脚本已改写为纯 ASCII，若仍出现说明文件被某种编辑器改坏，重新 `git pull` 取最新 `dev-windows.ps1`。
- **想重置数据**：删掉 `yd-backend/yd_lite.db`，重新双击 `run-dev.bat` 即可重建。
- **Redis 不需要**：Dev/Lite 模式验证码走内存字典，无需真实 Redis。
- **后台页面空白**：后台 vite base 是 `/admin/`，请访问 `http://localhost:5181/admin/`（不是根路径）。

## 七、已验证
后端启动自建于 ORM 建表 + 幂等种子（与 MySQL 模式共用 `app/db/seed.py`）；
沙箱（Git Bash）中以 SQLite 模式完成三端 + 后端 API 全链路冒烟：
admin 登录 → 产品/订单/会员/预约管理；会员登录 → 我的订单/个人中心；
公开产品列表；图形验证码生成。后台 `/admin/` 路径 nginx 配置已在 Docker 版修正。
