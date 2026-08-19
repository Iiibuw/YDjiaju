"""健康检查端点。M0 阶段最小可用。"""
from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings

router = APIRouter()


@router.get("/health")
def health():
    """基础健康检查（含 DB ping）。"""
    db_ok = False
    db_error = None
    try:
        # 延迟导入，避免启动时强依赖
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_error = str(e)[:120]

    return {
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "env": settings.APP_ENV,
        "db_ok": db_ok,
        "db_error": db_error,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
