@echo off
chcp 65001 >nul 2>&1
setlocal
rem Add common uv / node install paths to PATH (double-click may have a limited PATH)
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%APPDATA%\npm;%LOCALAPPDATA%\Programs\Python\Launcher;%PATH%"
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\dev-windows.ps1"
pause
