"""YD 家居后端入口。FastAPI 应用工厂。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动/关闭钩子。"""
    print(f"[{settings.APP_NAME}] startup · env={settings.APP_ENV}")
    yield
    print(f"[{settings.APP_NAME}] shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS：本地开发允许所有源（生产收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["health"])


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": app.version,
        "status": "ok",
    }
