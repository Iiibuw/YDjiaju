"""应用配置。pydantic-settings 读环境变量。"""
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用
    APP_NAME: str = "YD Furniture API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库
    DB_TYPE: str = Field(default="mysql")  # 'mysql' | 'sqlite'
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "yd_furniture"
    DB_PATH: str = "./yd_lite.db"  # SQLite 文件路径（lite 模式用）

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # JWT
    JWT_SECRET: str = Field(default="change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 120

    # 验证码
    CAPTCHA_EXPIRE_SECONDS: int = 300
    CAPTCHA_MAX_FAILED_ATTEMPTS: int = 5
    CAPTCHA_LOCK_MINUTES: int = 15

    # CORS（字符串，逗号分隔）
    CORS_ORIGINS: str = "*"

    @property
    def database_url(self) -> str:
        if self.DB_TYPE.lower() == "sqlite":
            # Lite 模式：用本地 SQLite 文件，零依赖
            db_path = Path(self.DB_PATH).resolve()
            return f"sqlite:///{db_path}"
        # MySQL 模式（生产）。账号/密码含特殊字符（如 @）必须用 quote_plus 编码，
        # 否则 SQLAlchemy 会把 @ 误判为「主机分隔符」而解析出错误的连接串。
        user = quote_plus(self.DB_USER)
        pw = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{user}:{pw}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    @property
    def is_sqlite(self) -> bool:
        return self.DB_TYPE.lower() == "sqlite"

    @property
    def redis_url(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


# 单例
settings = get_settings()
