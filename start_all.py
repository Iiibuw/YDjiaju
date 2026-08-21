# -*- coding: utf-8 -*-
"""
YD 家具 · 一键启动脚本
启动三个服务:后端 API(8000) + 前台官网(5180) + 后台管理(5181)
已运行的服务会自动跳过;全部就绪后自动打开浏览器。
"""
import os
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # yd-furniture/
BACKEND = ROOT / "yd-backend"
FRONTEND = ROOT / "yd-frontend"
ADMIN = ROOT / "yd-admin"
LOG_DIR = ROOT / "logs"

PYTHON = BACKEND / ".venv" / "Scripts" / "python.exe"   # 后端 venv,一定存在
NODE = shutil.which("node") or r"C:\Users\纤云弄巧\.workbuddy\binaries\node\versions\22.22.2\node.exe"

SERVICES = [
    {
        "name": "后端 API",
        "port": 8000,
        "cwd": BACKEND,
        "cmd": [str(PYTHON), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        "url": "http://localhost:8000/api/v1/auth/captcha",
    },
    {
        "name": "前台官网",
        "port": 5180,
        "cwd": FRONTEND,
        "cmd": [NODE, str(FRONTEND / "node_modules" / "vite" / "bin" / "vite.js"), "--host", "0.0.0.0", "--port", "5180"],
        "url": "http://localhost:5180/",
    },
    {
        "name": "后台管理",
        "port": 5181,
        "cwd": ADMIN,
        "cmd": [NODE, str(ADMIN / "node_modules" / "vite" / "bin" / "vite.js"), "--host", "0.0.0.0", "--port", "5181"],
        "url": "http://localhost:5181/admin/login",
    },
]


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    print("=" * 56)
    print("  YD 家具 · 一键启动(后端 8000 / 前台 5180 / 后台 5181)")
    print("=" * 56)

    # 依赖检查
    if not PYTHON.exists():
        print(f"[错误] 找不到后端 Python:{PYTHON}")
        return 1
    for svc in SERVICES:
        if "vite.js" in svc["cmd"][1]:
            vite_js = svc["cmd"][1]
            if not Path(vite_js).exists():
                print(f"[错误] 找不到 vite:{vite_js}")
                return 1
    if not NODE:
        print("[错误] 找不到 node,请安装 Node.js 22+")
        return 1

    LOG_DIR.mkdir(exist_ok=True)

    for svc in SERVICES:
        if port_in_use(svc["port"]):
            print(f"[已运行] {svc['name']} (端口 {svc['port']} 已被占用,跳过启动)")
            continue
        log_path = LOG_DIR / f"{svc['port']}.log"
        log = open(log_path, "a", encoding="utf-8", errors="replace")
        log.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} 启动 =====\n")
        log.flush()
        proc = subprocess.Popen(
            svc["cmd"],
            cwd=str(svc["cwd"]),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        print(f"[启动中] {svc['name']}  PID={proc.pid}  日志: logs/{svc['port']}.log")

    # 等待全部就绪(最多 30s)
    print("-" * 56)
    ok = True
    for svc in SERVICES:
        for _ in range(60):
            if port_in_use(svc["port"]):
                print(f"[就绪] {svc['name']} → {svc['url']}")
                break
            time.sleep(0.5)
        else:
            print(f"[超时] {svc['name']} 未就绪,请看 logs/{svc['port']}.log")
            ok = False

    print("-" * 56)
    if ok:
        time.sleep(1)
        print("正在打开浏览器…")
        webbrowser.open("http://localhost:5180/")          # 前台官网
        webbrowser.open("http://localhost:5181/admin/login")  # 后台管理
        print()
        print("  前台官网  http://localhost:5180")
        print("  后台管理  http://localhost:5181/admin/login  (admin / admin123)")
        print()
        print("  服务在后台运行,本窗口可以关闭。")
        print("  停止服务:任务管理器结束 python/node 进程,或再次运行本脚本不会重复启动。")
    else:
        print("部分服务未就绪,请检查上方日志提示。")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
