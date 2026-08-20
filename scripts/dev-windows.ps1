# YD 家具 — Windows 原生开发启动脚本（MySQL 模式，无 Docker 依赖）
# 用法：双击根目录 run-dev.bat（推荐）；或右键本脚本「使用 PowerShell 运行」
# 前提：
#   1) 本机已安装并启动 MySQL 8.0（默认端口 3306）
#   2) 本机已安装 Python(含 uv) 与 Node.js(含 npm)
#
# 本脚本会：
#   1) 生成 yd-backend/.env.mysql 并复制为 .env（指向本机 MySQL）
#   2) 预检 MySQL 连通性（连不上会给出明确修改指引）
#   3) 初始化数据库（建库 yd_furniture + 14 张表 + 种子数据）
#   4) 启动后端(8000) / 前台(5180) / 后台(5181) 三个独立窗口
#
# ⚠️ 若你的 MySQL 账号/密码不是默认的 yd / yd_secret_2026，
#    请先编辑 yd-backend/.env.mysql 中的 DB_USER / DB_PASSWORD 再运行本脚本。

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host ""
Write-Host "=== YD 家具 — Windows 原生启动（MySQL 模式，无 Docker）==="
Write-Host ""

# ===== 0. 工具链预检 =====
function Test-Tool {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "❌ 未找到命令: $Name" -ForegroundColor Red
        Write-Host "   $Hint" -ForegroundColor Yellow
        return $false
    }
    return $true
}
$toolsOk = $true
if (-not (Test-Tool "uv"   "请安装 uv 并加入 PATH：https://docs.astral.sh/uv/getting-started/installation/ （或执行 'pip install uv'）")) { $toolsOk = $false }
if (-not (Test-Tool "node" "请安装 Node.js（含 npm）：https://nodejs.org/")) { $toolsOk = $false }
if (-not (Test-Tool "npm"  "请安装 Node.js（含 npm）：https://nodejs.org/")) { $toolsOk = $false }
if (-not $toolsOk) {
    Write-Host ""
    Write-Host "请安装上述工具后重跑 run-dev.bat。" -ForegroundColor Yellow
    pause
    exit 1
}

# ===== 0.5 选择包管理器（优先 pnpm，缺失则回落 npm）=====
if (Get-Command pnpm -ErrorAction SilentlyContinue) { $pkg = "pnpm" } else { $pkg = "npm" }
Write-Host "📦 检测到包管理器：$pkg （前端将用 '$pkg run dev' 启动）"

# ===== 1. 配置 .env 指向本地 MySQL =====
$envFile  = Join-Path $ROOT "yd-backend\.env"
$envMysql = Join-Path $ROOT "yd-backend\.env.mysql"

if (-not (Test-Path $envMysql)) {
    Write-Host "📝 生成 .env.mysql 模板..."
    @"
# MySQL 模式 — 指向本机 localhost
# ⚠️ 若你的 MySQL 账号/密码不是下面的值，请修改 DB_USER / DB_PASSWORD 后重跑本脚本
APP_NAME=YD Furniture API
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=yd
DB_PASSWORD=yd_secret_2026
DB_NAME=yd_furniture

# Redis（Lite/Dev 模式：验证码走内存字典，无需真实 Redis）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

JWT_SECRET=local-dev-secret-please-change
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=120

CAPTCHA_EXPIRE_SECONDS=300
CAPTCHA_MAX_FAILED_ATTEMPTS=5
CAPTCHA_LOCK_MINUTES=15

CORS_ORIGINS=http://localhost:5180,http://localhost:5181
"@ | Out-File -FilePath $envMysql -Encoding utf8
}

Copy-Item $envMysql $envFile -Force
Write-Host "✅ .env 已指向本地 MySQL (localhost)"

# ===== 2. MySQL 连通性预检 =====
Write-Host ""
Write-Host "🔌 预检 MySQL 连通性..."

# 解析 .env.mysql 中的连接参数
$cfg = @{}
Get-Content $envMysql | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*)\s*$') { $cfg[$matches[1]] = $matches[2] }
}
$dbHost = $cfg['DB_HOST']; $dbPort = $cfg['DB_PORT']
$dbUser = $cfg['DB_USER']; $dbPass = $cfg['DB_PASSWORD']

$probe = Join-Path $ROOT "yd-backend\scripts\_mysql_probe.py"
@"
import sys, pymysql
host, port, user, pw = sys.argv[1:5]
try:
    pymysql.connect(host=host, port=int(port), user=user, password=pw, connect_timeout=5)
    print("PING_OK")
except Exception as e:
    print("PING_FAIL", repr(e))
"@ | Out-File -FilePath $probe -Encoding utf8

# 必须在 yd-backend 目录下执行，否则 uv run 找不到 pyproject 依赖
Push-Location (Join-Path $ROOT "yd-backend")
try {
    $probeOut = & uv run python $probe $dbHost $dbPort $dbUser $dbPass 2>&1
} finally {
    Pop-Location
}
Remove-Item $probe -Force -ErrorAction SilentlyContinue

if ($probeOut -notmatch "PING_OK") {
    Write-Host "❌ 无法连接到本机 MySQL：" -ForegroundColor Red
    Write-Host "   $probeOut" -ForegroundColor Red
    Write-Host ""
    Write-Host "请检查：" -ForegroundColor Yellow
    Write-Host "  1) MySQL 服务是否已启动（可在『服务』里看 MySQL80，或命令行 net start mysql）"
    Write-Host "  2) 端口是否为 3306（对应 DB_PORT）"
    Write-Host "  3) 账号密码是否正确：默认 yd / yd_secret_2026"
    Write-Host "     若不同，请编辑 yd-backend/.env.mysql 的 DB_USER / DB_PASSWORD 后重跑"
    Write-Host ""
    pause
    exit 1
}
Write-Host "✅ MySQL 连通正常"

# ===== 3. 初始化 MySQL（建库 + 建表 + 种子）=====
Write-Host ""
Write-Host "🗄️  初始化 MySQL 数据..."
Push-Location (Join-Path $ROOT "yd-backend")
try {
    & uv run python scripts/init_lite.py --type=mysql
} catch {
    Write-Host "❌ MySQL 初始化失败：$_" -ForegroundColor Red
    Write-Host "   常见原因：该账号无建库权限，或数据库已存在但表结构不兼容。" -ForegroundColor Yellow
    Write-Host "   如需重建，可手动 DROP DATABASE yd_furniture 后重跑本脚本。" -ForegroundColor Yellow
    Pop-Location
    pause
    exit 1
}
Pop-Location

# ===== 4. 启动后端 =====
Write-Host ""
Write-Host "🚀 启动后端（8000）..."
$backendScript = "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\yd-backend'; $backendScript" -WindowStyle Normal

# ===== 5. 启动前台 =====
Write-Host "🌐 启动前台（5180）..."
$frontendScript = "cd '$ROOT\yd-frontend'; $pkg run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# ===== 6. 启动后台 =====
Write-Host "🔧 启动后台（5181）..."
$adminScript = "cd '$ROOT\yd-admin'; $pkg run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminScript -WindowStyle Normal

Write-Host ""
Write-Host "============================================="
Write-Host "✅ 全栈启动中，请等待约 10 秒后访问："
Write-Host "   前台：  http://localhost:5180"
Write-Host "   后台：  http://localhost:5181"
Write-Host "   后端：  http://localhost:8000"
Write-Host "   API 文档：http://localhost:8000/docs"
Write-Host ""
Write-Host "   后台账号： admin / admin123"
Write-Host "   会员账号： 13800138001 / member123"
Write-Host ""
Write-Host "3 个独立 PowerShell 窗口已弹出，关闭此窗口不会停服务"
Write-Host "============================================="
pause
