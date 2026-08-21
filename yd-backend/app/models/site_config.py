"""站点配置字典（键值对）。

字段以数据库设计文档 §4.3.8 为准。
"""
from sqlalchemy import BigInteger, Enum, ForeignKey, Index, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import AuditMixin


class SiteConfig(Base, AuditMixin):
    __tablename__ = "site_configs"
    __table_args__ = (
        UniqueConstraint("config_key", name="UNQ_site_configs_key"),
        Index("IDX_site_configs_category", "category"),
        Index("IDX_site_configs_is_activate", "is_activate"),
        Index("IDX_site_configs_created_date", "created_date"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "comment": "站点配置字典",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(String(64), nullable=False, comment="配置键")
    config_value: Mapped[str] = mapped_column(Text, nullable=False, comment="配置值")
    value_type: Mapped[str] = mapped_column(
        Enum("string", "number", "json", "bool", name="enum_site_config_value_type"),
        nullable=False,
        default="string",
        server_default="string",
        comment="值类型",
    )
    category: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="配置分类")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="说明")
    updated_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        comment="最后修改人",
    )
