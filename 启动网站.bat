@echo off
title YD Furniture - Start All Services
cd /d %~dp0
echo Starting YD Furniture services...
if exist "yd-backend\.venv\Scripts\python.exe" (
  "yd-backend\.venv\Scripts\python.exe" start_all.py
) else (
  python start_all.py
)
echo.
pause
