"""SQLAlchemy 引擎与 Session 工厂（M1 阶段启用，M0 留接口）。"""
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _build_engine() -> Engine:
    if settings.is_sqlite:
        # SQLite：单文件，无池，用 StaticPool 让 in-memory 也能跨连接
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool if ":memory:" in settings.database_url else None,
            echo=settings.DEBUG,
            future=True,
        )
    # MySQL（生产）
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG,
        future=True,
    )


engine = _build_engine()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """FastAPI 依赖：每个请求一个 Session。"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
