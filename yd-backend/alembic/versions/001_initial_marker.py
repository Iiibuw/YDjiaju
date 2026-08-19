"""首版迁移占位说明

⚠️ 注意：本次首版 schema 通过 `数据库设计文档_install_all.sql` 一键执行（34 张表 + 触发器 + 视图 + 种子数据）。
Alembic 仅负责增量迁移（002+），避免与 install_all.sql 双源同步漂移。

历史：
- 2026-08-19: install_all.sql 已写入完整 schema
- 后续 M2 起：每次模型变更用 `alembic revision --autogenerate -m "..."` 生成迁移
"""
revision = "001_initial_marker"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """占位 — 实际 schema 由 install_all.sql 管理。"""
    pass


def downgrade() -> None:
    """占位 — 若需回滚应执行 install_all.sql 的清理 SQL。"""
    pass
