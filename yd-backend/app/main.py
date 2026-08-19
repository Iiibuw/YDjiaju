"""YD 家居后端入口。FastAPI 应用工厂。"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import (
    admin_cases,
    admin_depts,
    admin_jobs,
    admin_members,
    admin_news,
    admin_products,
    auth,
    health,
    public_cases,
    public_jobs,
    public_members,
    public_news,
    public_products,
)
from app.core.config import settings
from app.schemas.common import ApiResponse

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger("yd")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup", app=settings.APP_NAME, env=settings.APP_ENV, version=app.version)
    yield
    log.info("shutdown", app=settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 全局异常处理 =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一 HTTPException 为 ApiResponse 包装。"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            code=exc.status_code,
            message=str(exc.detail),
            trace_id=request.headers.get("x-request-id"),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """兜底 500：避免泄露内部细节。"""
    log.exception("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="服务内部错误",
            trace_id=request.headers.get("x-request-id"),
        ).model_dump(),
    )


# ===== 路由注册 =====

API_V1_PREFIX = "/api/v1"

# 公共 / 后台接口统一挂在 /api/v1 下
app.include_router(health.router, prefix=API_V1_PREFIX, tags=["health"])
app.include_router(auth.router, prefix=API_V1_PREFIX, tags=["auth"])
app.include_router(public_products.router, prefix=API_V1_PREFIX, tags=["public_products"])
app.include_router(public_cases.router, prefix=API_V1_PREFIX, tags=["public_cases"])
app.include_router(public_news.router, prefix=API_V1_PREFIX, tags=["public_news"])
app.include_router(public_jobs.router, prefix=API_V1_PREFIX, tags=["public_jobs"])
app.include_router(public_members.router, prefix=API_V1_PREFIX, tags=["public_members"])
app.include_router(admin_products.router, prefix=API_V1_PREFIX, tags=["admin_products"])
app.include_router(admin_news.router, prefix=API_V1_PREFIX, tags=["admin_news"])
app.include_router(admin_jobs.router, prefix=API_V1_PREFIX, tags=["admin_jobs"])
app.include_router(admin_cases.router, prefix=API_V1_PREFIX, tags=["admin_cases"])
app.include_router(admin_depts.router, prefix=API_V1_PREFIX, tags=["admin_depts"])
app.include_router(admin_members.router, prefix=API_V1_PREFIX, tags=["admin_members"])


@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "version": app.version,
        "status": "ok",
        "swagger": "/docs" if settings.DEBUG else "disabled",
    }
