# YD Furniture - Windows Dev Starter (MySQL mode, no Docker required)
# Usage: double-click run-dev.bat in project root (recommended);
#        or right-click this script and "Run with PowerShell".
# Prerequisites:
#   1) MySQL 8.0 installed and running locally (default port 3306)
#   2) Python (with uv) and Node.js (with npm) installed
#
# This script will:
#   1) Generate yd-backend/.env.mysql and copy to .env (pointing to local MySQL)
#   2) Probe MySQL connectivity (clear fix guidance if unreachable)
#   3) Initialize database (create yd_furniture + 14 tables + seed data)
#   4) Launch backend (8000) / frontend (5180) / admin (5181) in 3 separate windows
#
# NOTE: MySQL creds default to the Docker MySQL container (Iiibuw / your password).
#       If different, edit DB_USER/DB_PASSWORD in yd-backend/.env.mysql BEFORE running.

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

Write-Host ""
Write-Host "=== YD Furniture - Windows Dev Starter (MySQL mode, no Docker) ==="
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

# ===== 1. Configure .env to point to local MySQL =====
$envFile  = Join-Path $ROOT "yd-backend\.env"
$envMysql = Join-Path $ROOT "yd-backend\.env.mysql"

if (-not (Test-Path $envMysql)) {
    Write-Host "[INFO] Generating .env.mysql template..."
    @"
# MySQL mode - pointing to localhost
# NOTE: If your MySQL user/password is NOT the values below, edit DB_USER/DB_PASSWORD before re-running this script.
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

# Redis (Lite/Dev mode: captcha uses in-memory dict, no real Redis needed)
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
Write-Host "[OK] .env -> local MySQL (localhost)"

# ===== 2. MySQL connectivity probe =====
Write-Host ""
Write-Host "[PROBE] Testing MySQL connectivity..."

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

# Must run in yd-backend so uv run finds pyproject deps
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
    Write-Host "  1) MySQL service is running (check Services for MySQL80, or 'net start mysql')"
    Write-Host "  2) Port is 3306 (DB_PORT)"
    Write-Host "  3) User/password correct. Default: Iiibuw / (your Docker MySQL password)"
    Write-Host "     If different, edit DB_USER/DB_PASSWORD in yd-backend/.env.mysql and re-run"
    Write-Host ""
    pause
    exit 1
}
Write-Host "[OK] MySQL reachable"

# ===== 3. Initialize MySQL (create db + tables + seed) =====
Write-Host ""
Write-Host "[INIT] Initializing MySQL database..."
Push-Location (Join-Path $ROOT "yd-backend")
try {
    & uv run python scripts/init_lite.py --type=mysql
} catch {
    Write-Host "[ERROR] MySQL init failed: $_" -ForegroundColor Red
    Write-Host "        Common causes: account lacks CREATE DATABASE permission, or existing db schema is incompatible." -ForegroundColor Yellow
    Write-Host "        To rebuild: DROP DATABASE yd_furniture manually, then re-run this script." -ForegroundColor Yellow
    Pop-Location
    pause
    exit 1
}
Pop-Location

# ===== 4. Launch backend =====
Write-Host ""
Write-Host "[START] Backend (port 8000)..."
$backendScript = "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\yd-backend'; $backendScript" -WindowStyle Normal

# ===== 5. Launch frontend =====
Write-Host "[START] Frontend (port 5180)..."
$frontendScript = "cd '$ROOT\yd-frontend'; $pkg run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

# ===== 6. Launch admin =====
Write-Host "[START] Admin (port 5181)..."
$adminScript = "cd '$ROOT\yd-admin'; $pkg run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminScript -WindowStyle Normal

Write-Host ""
Write-Host "============================================="
Write-Host "[OK] All services starting. Wait ~10 seconds then visit:"
Write-Host "   Frontend : http://localhost:5180"
Write-Host "   Admin    : http://localhost:5181"
Write-Host "   Backend  : http://localhost:8000"
Write-Host "   API docs : http://localhost:8000/docs"
Write-Host ""
Write-Host "   Admin login   : admin / admin123"
Write-Host "   Member login  : 13800138001 / member123"
Write-Host ""
Write-Host "3 separate PowerShell windows opened. Closing this window will not stop them."
Write-Host "============================================="
pause