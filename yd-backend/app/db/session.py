"""SQLAlchemy 引擎与 Session 工厂（M1 阶段启用，M0 留接口）。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# 注意：M0 时 DB 尚未建好，连接会失败。health 端点会捕获。
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """FastAPI 依赖：每个请求一个 Session。"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
