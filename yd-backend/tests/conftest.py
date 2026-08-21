"""pytest 共享夹具：独立 SQLite 测试库 + 幂等种子 + TestClient。

注意：环境变量必须在任何 app 模块导入之前设置（config 在导入时读取）。
"""
import os

os.environ["APP_ENV"] = "test"  # 跳过 lifespan 的建表/种子（由本文件自行初始化）
os.environ["DB_TYPE"] = "sqlite"
os.environ["DB_PATH"] = "./test_yd.db"
os.environ["DEBUG"] = "True"  # 验证码走 DEV_CAPTCHA_CODE 固定码
os.environ["DEV_CAPTCHA_CODE"] = "ABCD"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

import app.models  # noqa: F401  # 注册全部模型到 Base.metadata
from app.db import session as dbsession
from app.db.seed import ensure_schema, seed_initial_data

# 每次测试会话用全新测试库，保证种子一致
if os.path.exists("./test_yd.db"):
    os.remove("./test_yd.db")
ensure_schema()
with dbsession.SessionLocal() as db:
    seed_initial_data(db)

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient（启动/关闭 lifespan）。"""
    with TestClient(app) as c:
        yield c
