# YD Furniture - Windows Dev Starter
# Default mode: SQLite (zero external dependencies, no Docker, no MySQL needed).
# Optional mode: MySQL (pass -MySQL when you have a local MySQL 8.0 running).
#
# How to run:
#   - Double-click run-dev.bat in project root (recommended, default = SQLite)
#   - Or: right-click this script and "Run with PowerShell"
#   - For MySQL mode: run-dev.bat -MySQL   (or: powershell -File dev-windows.ps1 -MySQL)
#
# This script will:
#   1) Pick the env file (.env.sqlite for default, .env.mysql for -MySQL)
#   2) (MySQL only) Probe MySQL connectivity with clear fix guidance
#   3) Initialize database (create 14 tables + seed data)
#   4) Launch backend/FastAPI (8000) / frontend/React (5180) / admin/React (5181) in 3 windows

param([switch]$MySQL)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$mode = if ($MySQL) { "MySQL" } else { "SQLite" }

Write-Host ""
Write-Host "=== YD Furniture - Windows Dev Starter ($mode mode) ==="
Write-Host ""

# ===== 0. Toolchain preflight =====
function Test-Tool {
    param([string]$Name, [string]$Hint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Command not found: $Name" -ForegroundColor Red
        Write-Host "        $Hint" -ForegroundColor Yellow
        return $false
    }
    return $true
}
$toolsOk = $true
if (-not (Test-Tool "uv"   "Install uv and add to PATH: https://docs.astral.sh/uv/getting-started/installation/ (or 'pip install uv')")) { $toolsOk = $false }
if (-not (Test-Tool "node" "Install Node.js (with npm): https://nodejs.org/")) { $toolsOk = $false }
if (-not (Test-Tool "npm"  "Install Node.js (with npm): https://nodejs.org/")) { $toolsOk = $false }
if (-not $toolsOk) {
    Write-Host ""
    Write-Host "Please install the missing tools, then re-run run-dev.bat." -ForegroundColor Yellow
    pause
    exit 1
}

# ===== 0.5 Choose package manager (pnpm preferred, npm fallback) =====
if (Get-Command pnpm -ErrorAction SilentlyContinue) { $pkg = "pnpm" } else { $pkg = "npm" }
Write-Host "[INFO] Package manager: $pkg (frontend will use '$pkg run dev')"

# ===== 1. Configure .env =====
$envFile = Join-Path $ROOT "yd-backend\.env"

if ($MySQL) {
    # ---- MySQL mode ----
    $envMysql = Join-Path $ROOT "yd-backend\.env.mysql"
    if (-not (Test-Path $envMysql)) {
        Write-Host "[INFO] Generating .env.mysql template..."
        $mysqlEnv = @"
APP_NAME=YD Furniture API
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=Iiibuw
DB_PASSWORD=Yd@1234567
DB_NAME=yd_furniture

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
"@
        $mysqlEnv | Out-File -FilePath $envMysql -Encoding ascii
    }
    Copy-Item $envMysql $envFile -Force
    Write-Host "[OK] .env -> local MySQL (127.0.0.1:3306)"

    # ---- MySQL connectivity probe ----
    Write-Host ""
    Write-Host "[PROBE] Testing MySQL connectivity..."
    $cfg = @{}
    Get-Content $envMysql | ForEach-Object {
        if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*)\s*$') { $cfg[$matches[1]] = $matches[2] }
    }
    $dbHost = $cfg['DB_HOST']; $dbPort = $cfg['DB_PORT']
    $dbUser = $cfg['DB_USER']; $dbPass = $cfg['DB_PASSWORD']

    $probe = Join-Path $ROOT "yd-backend\scripts\_mysql_probe.py"
    $probeSrc = @"
import sys, pymysql
host, port, user, pw = sys.argv[1:5]
try:
    pymysql.connect(host=host, port=int(port), user=user, password=pw, connect_timeout=5)
    print("PING_OK")
except Exception as e:
    print("PING_FAIL", repr(e))
"@
    $probeSrc | Out-File -FilePath $probe -Encoding ascii

    Push-Location (Join-Path $ROOT "yd-backend")
    try {
        $probeOut = & uv run python $probe $dbHost $dbPort $dbUser $dbPass 2>&1
    } finally {
        Pop-Location
    }
    Remove-Item $probe -Force -ErrorAction SilentlyContinue

    if ($probeOut -notmatch "PING_OK") {
        Write-Host "[ERROR] Cannot connect to local MySQL:" -ForegroundColor Red
        Write-Host "        $probeOut" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "  1) MySQL 8.0 service is running (Services -> MySQL80, or 'net start mysql')"
        Write-Host "  2) Port is 3306 (DB_PORT in yd-backend/.env.mysql)"
        Write-Host "  3) User/password correct (default Iiibuw / your MySQL password)"
        Write-Host "     Edit DB_USER/DB_PASSWORD in yd-backend/.env.mysql then re-run: run-dev.bat -MySQL"
        Write-Host ""
        pause
        exit 1
    }
    Write-Host "[OK] MySQL reachable"
} else {
    # ---- SQLite mode (default, zero deps) ----
    $envSqlite = Join-Path $ROOT "yd-backend\.env.sqlite"
    if (-not (Test-Path $envSqlite)) {
        Write-Host "[INFO] Generating .env.sqlite template..."
        $sqliteEnv = @"
APP_NAME=YD Furniture API (Lite)
APP_ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

DB_TYPE=sqlite
DB_PATH=./yd_lite.db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

JWT_SECRET=lite-dev-secret-change-in-prod
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRE_MINUTES=120

CAPTCHA_EXPIRE_SECONDS=300
CAPTCHA_MAX_FAILED_ATTEMPTS=5
CAPTCHA_LOCK_MINUTES=15

CORS_ORIGINS=*
"@
        $sqliteEnv | Out-File -FilePath $envSqlite -Encoding ascii
    }
    Copy-Item $envSqlite $envFile -Force
    Write-Host "[OK] .env -> local SQLite (zero external dependencies, no Docker/MySQL needed)"
}

# ===== 2. Initialize database (create tables + seed) =====
Write-Host ""
Write-Host "[INIT] Initializing database ($mode)..."
Push-Location (Join-Path $ROOT "yd-backend")
try {
    if ($MySQL) {
        & uv run python scripts/init_lite.py --type=mysql
    } else {
        & uv run python scripts/init_lite.py
    }
} catch {
    Write-Host "[ERROR] Database init failed: $_" -ForegroundColor Red
    if (-not $MySQL) {
        Write-Host "        SQLite mode should never fail to connect. If you see schema errors," -ForegroundColor Yellow
        Write-Host "        delete yd-backend/yd_lite.db and re-run this script." -ForegroundColor Yellow
    } else {
        Write-Host "        Common cause: MySQL account lacks CREATE DATABASE permission." -ForegroundColor Yellow
        Write-Host "        Fix: DROP DATABASE yd_furniture manually, then re-run." -ForegroundColor Yellow
    }
    Pop-Location
    pause
    exit 1
}
Pop-Location

# ===== 3. Launch backend (FastAPI) =====
Write-Host ""
Write-Host "[START] Backend / FastAPI (port 8000)..."
$backendScript = "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\yd-backend'; $backendScript" -WindowStyle Normal

# ===== 4. Launch frontend (React) =====
Write-Host "[START] Frontend / React (port 5180)..."
$frontendScript = "cd '$ROOT\yd-frontend'; $pkg run dev -- --port 5180 --host 127.0.0.1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# ===== 5. Launch admin (React, base /admin/) =====
Write-Host "[START] Admin / React (port 5181, base /admin/)..."
$adminScript = "cd '$ROOT\yd-admin'; $pkg run dev -- --port 5181 --host 127.0.0.1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminScript -WindowStyle Normal

Write-Host ""
Write-Host "============================================="
Write-Host "[OK] All services starting. Wait ~10 seconds then visit:"
Write-Host "   Frontend : http://localhost:5180"
Write-Host "   Admin    : http://localhost:5181/admin/"
Write-Host "   Backend  : http://localhost:8000"
Write-Host "   API docs : http://localhost:8000/docs"
Write-Host ""
Write-Host "   Admin login   : admin / admin123"
Write-Host "   Member login  : 13800138001 / member123"
Write-Host ""
Write-Host "3 separate PowerShell windows opened. Closing this window will not stop them."
Write-Host "============================================="
pause
