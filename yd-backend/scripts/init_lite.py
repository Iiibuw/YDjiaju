"""Lite 模式数据库初始化 + 种子数据。

用法（venv 激活后）：
    cd yd-backend
    # SQLite 模式（默认，无需 MySQL）
    cp .env.lite .env
    uv run python scripts/init_lite.py

    # MySQL 模式（指向 .env 里的 DB_HOST，Docker 起不来时用本机 localhost）
    uv run python scripts/init_lite.py --type=mysql

会：
1. (sqlite) 删除旧 yd_lite.db | (mysql) drop_all + create_all
2. 通过 Base.metadata.create_all 重建 14 张表（M1 + M2 全量）
3. 调用 app.db.seed.seed_initial_data 灌入种子数据
   （admin/超管 + 1 部门 + 1 角色 + 类目 + 产品 + 资讯 + 招聘 + 案例 + 部门 + 会员 + 留言 + 订单 + 预约）
   种子逻辑与 Docker 启动时的 lifespan 共用，避免漂移。
"""
import sys
from pathlib import Path

# 把项目根加入路径
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ====== 解析 --type 参数（默认 sqlite） ======
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--type", choices=["sqlite", "mysql"], default="sqlite", help="数据库类型")
_args = ap.parse_args()
DB_TYPE = _args.type

# ====== 清空 pydantic-settings 缓存（让 .env 重新生效） ======
from app.core.config import get_settings
from app.core.security import hash_password

get_settings.cache_clear()
from app.core import config as _cfg

if DB_TYPE == "sqlite":
    _cfg.settings.DB_TYPE = "sqlite"
    _cfg.settings.DB_PATH = str(ROOT / "yd_lite.db")
else:
    # MySQL：保留 .env 里的 DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME
    # 默认 .env.example 已经设好（DB_HOST=mysql）；本机用 .env（DB_HOST=localhost）
    print(f"  → MySQL 模式：{_cfg.settings.DB_HOST}:{_cfg.settings.DB_PORT}/{_cfg.settings.DB_NAME}")

# 重新加载 settings 确保生效
get_settings.cache_clear()

# 重新构建 engine
from app.db import session as _session
from app.db.base import Base
from sqlalchemy import create_engine

_session.engine.dispose()
if _cfg.settings.is_sqlite:
    _session.engine = create_engine(
        _cfg.settings.database_url,
        connect_args={"check_same_thread": False},
        echo=_cfg.settings.DEBUG,
        future=True,
    )
else:
    # MySQL：先尝试 server-level 连接确保库存在（CREATE DATABASE IF NOT EXISTS）
    _session.engine = create_engine(
        _cfg.settings.database_url,
        echo=_cfg.settings.DEBUG,
        pool_pre_ping=True,
        future=True,
    )
_session.SessionLocal.configure(bind=_session.engine)

# ====== MySQL 模式：确保数据库存在 ======
if not _cfg.settings.is_sqlite:
    from sqlalchemy import text
    server_url = (
        f"mysql+pymysql://{_cfg.settings.DB_USER}:{_cfg.settings.DB_PASSWORD}"
        f"@{_cfg.settings.DB_HOST}:{_cfg.settings.DB_PORT}/?charset=utf8mb4"
    )
    try:
        srv = create_engine(server_url, future=True)
        with srv.connect() as conn:
            conn.execute(text(
                f"CREATE DATABASE IF NOT EXISTS `{_cfg.settings.DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            ))
            conn.commit()
        srv.dispose()
        print(f"📍 MySQL 库 `{_cfg.settings.DB_NAME}` 已就绪")
    except Exception as e:
        print(f"⚠️  无法自动建库（可能权限不足）：{e}")
        print(f"   请手动执行：CREATE DATABASE {_cfg.settings.DB_NAME} CHARACTER SET utf8mb4;")

# ====== 删除旧数据库 ======
DB_FILE = ROOT / "yd_lite.db"

print(f"\n📍 URL = {_cfg.settings.database_url}")

if _cfg.settings.is_sqlite:
    if DB_FILE.exists():
        print(f"📍 SQLite 文件已存在：{DB_FILE.name}（将清空表）")
    else:
        print(f"📍 新建 SQLite 文件：{DB_FILE.name}")
else:
    print(f"📍 MySQL 模式：drop_all + create_all（不会真删数据库，只清表）")

print("\n🏗️  重建表结构...")

# 先 import 所有模型确保 metadata 注册
import app.models  # noqa: F401

# 删表 + 建表
Base.metadata.drop_all(bind=_session.engine)
Base.metadata.create_all(bind=_session.engine)
print(f"  ✓ 创建 {len(Base.metadata.tables)} 张表：")
for t in sorted(Base.metadata.tables.keys()):
    print(f"    - {t}")

# ====== 种子数据（与 Docker 启动时共用同一份逻辑） ======
print("\n🌱 灌入种子数据...")
from app.db.seed import seed_initial_data

with _session.SessionLocal() as db:
    seeded = seed_initial_data(db)

if seeded:
    print("\n✅ Lite 数据库初始化完成！")
    print(f"   登录: admin / admin123")
else:
    print("\n⚠️  检测到已有 admin 数据，跳过种子（保持现有数据）。")
    print(f"   登录: admin / admin123")
