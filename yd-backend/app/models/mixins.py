"""通用字段 Mixin（与数据库设计文档 v1.1 字段约定一致）。

约定：
- id: BIGINT UNSIGNED 主键
- is_activate: TINYINT(1) NOT NULL DEFAULT 1（激活/禁用）
- created_at: BIGINT UNSIGNED NULL（创建人，FK → admin_users.id）
- created_date: DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) — MySQL；Lite 用 SQLite 时默认按整秒（精度由应用层兜底）
- updated_at: BIGINT UNSIGNED NULL（修改人，FK → admin_users.id）
- updated_date: DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)

兼容：
- MySQL 8：使用 CURRENT_TIMESTAMP(3) 子秒精度
- SQLite（Lite 模式）：用 CURRENT_TIMESTAMP（无子秒）
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, SmallInteger, event, func
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column


def _sqlite_compat_timestamp(column):
    """SQLite 不支持 CURRENT_TIMESTAMP(3) → 改写为 CURRENT_TIMESTAMP。"""
    if str(column.table.bind.dialect.name) == "sqlite":
        return func.current_timestamp()
    return func.current_timestamp(3)


class AuditMixin:
    """审计字段。所有业务表继承。"""

    is_activate: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1", comment="激活/禁用：1=激活 0=禁用")
    created_at: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="创建人（FK→admin_users.id）",
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="修改人（FK→admin_users.id）",
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="修改时间",
    )


class SoftDeleteMixin:
    """软删除字段。业务数据保留行。"""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True, comment="软删除时间")
    is_deleted: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0", comment="软删除标记")
