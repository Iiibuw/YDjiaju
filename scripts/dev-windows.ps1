# YD 家具 — Windows 原生开发启动脚本
# 用法：双击运行；或 PowerShell 里执行
# 前提：MySQL 8.0 已起在本机 3306 端口

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host ""
Write-Host "=== YD 家具 — Windows 原生启动（MySQL 模式）==="
Write-Host ""

# ===== 1. 配置 .env 指向本地 MySQL =====
$envFile = Join-Path $ROOT "yd-backend\.env"
$envMysql = Join-Path $ROOT "yd-backend\.env.mysql"

if (-not (Test-Path $envMysql)) {
    Write-Host "📝 生成 .env.mysql 模板..."
    @"
# MySQL 模式 — 指向本机 localhost
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

# Redis（未启用；验证码暂时走内存字典）
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

# ===== 2. 初始化 MySQL =====
Write-Host ""
Write-Host "🗄️  初始化 MySQL 数据..."
Push-Location (Join-Path $ROOT "yd-backend")
try {
    & uv run python scripts/init_lite.py --type=mysql
} catch {
    Write-Host "❌ MySQL 初始化失败：$_" -ForegroundColor Red
    Pop-Location
    pause
    exit 1
}

# ===== 3. 启动后端 =====
Write-Host ""
Write-Host "🚀 启动后端（8000）..."
$backendScript = "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\yd-backend'; $backendScript" -WindowStyle Normal

# ===== 4. 启动前台 =====
Write-Host "🌐 启动前台（5180）..."
$frontendScript = "cd '$ROOT\yd-frontend'; pnpm dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# ===== 5. 启动后台 =====
Write-Host "🔧 启动后台（5181）..."
$adminScript = "cd '$ROOT\yd-admin'; pnpm dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminScript -WindowStyle Normal

Pop-Location
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