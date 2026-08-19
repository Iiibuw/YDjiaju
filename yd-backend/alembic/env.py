"""Alembic 环境配置：从 app 导入 metadata，动态注入所有模型。
与 `app.db.base.Base.metadata` 同步，alembic revision --autogenerate 自动检测差异。
"""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.config import settings
from app.db.base import Base

# ⚠️ 必须显式 import 所有模型，autogenerate 才能发现新表/列
from app.models import (  # noqa: F401
    AdminUser,
    Case,
    Category,
    Dept,
    Product,
    Role,
    User,
)

config = context.config

# 从 app 配置覆盖 sqlalchemy.url
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """无 DB 连接时输出 SQL。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """连 DB 后执行迁移。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            render_as_batch=False,  # MySQL 直接 ALTER
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
