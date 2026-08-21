"""YD家居 Alembic 首版迁移脚本（精简版，仅 depts 表作为示例）

实际项目应将 install_all.sql 中的所有 CREATE TABLE 转换为 Alembic 操作。

Revision ID: 001_initial
Revises:
Create Date: 2026-08-18
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """升级：创建首版完整 schema。

    实际项目应按以下顺序逐张创建（参考 install_all.sql）：
    1. depts, roles, permissions, admin_users
    2. users, user_addresses, user_favorites, user_search_logs
    3. admin_roles, admin_regions, role_permissions
    4. categories, products, product_skus, product_images
    5. banners, cases, case_images, news, about_sections, about_images
    6. site_configs, downloads, chat_keywords
    7. jobs, job_applications
    8. appointments, messages, cart_items
    9. orders, order_items, payments
    10. stats_visit, audit_logs
    """
    # ===== depts 表示例 =====
    op.create_table(
        'depts',
        sa.Column('id', sa.BigInteger().with_variant(sa.Integer, 'sqlite'),
                  primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(64), nullable=False, comment='部门名称'),
        sa.Column('code', sa.String(32), nullable=True, comment='部门编码'),
        sa.Column('parent_id', sa.BigInteger().with_variant(sa.Integer, 'sqlite'),
                  nullable=True, comment='上级部门（自引用）'),
        sa.Column('sort', sa.Integer, nullable=False, server_default='0', comment='同级排序'),
        sa.Column('leader_id', sa.BigInteger().with_variant(sa.Integer, 'sqlite'),
                  nullable=True, comment='部门负责人'),
        sa.Column('path', sa.String(255), nullable=True, comment='层级路径（,1,3,7,）'),

        # 通用字段
        sa.Column('is_activate', sa.Boolean, nullable=False, server_default=sa.text('1'),
                  comment='激活/禁用'),
        sa.Column('created_at', sa.BigInteger().with_variant(sa.Integer, 'sqlite'),
                  nullable=True, comment='创建人'),
        sa.Column('created_date', sa.DateTime(timezone=False),
                  nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.BigInteger().with_variant(sa.Integer, 'sqlite'),
                  nullable=True, comment='修改人'),
        sa.Column('updated_date', sa.DateTime(timezone=False),
                  nullable=False, server_default=sa.func.now(),
                  server_onupdate=sa.func.now(), comment='修改时间'),

        sa.CheckConstraint('parent_id IS NULL OR parent_id <> id',
                           name='chk_depts_no_self_parent'),
        sa.ForeignKeyConstraint(['parent_id'], ['depts.id'],
                                name='fk_depts_parent', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['leader_id'], ['admin_users.id'],
                                name='fk_depts_leader', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_at'], ['admin_users.id'],
                                name='fk_depts_created_at', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_at'], ['admin_users.id'],
                                name='fk_depts_updated_at', ondelete='SET NULL'),

        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_comment='部门表（树形）',
    )

    # 索引
    op.create_index('IDX_depts_parent_id', 'depts', ['parent_id'])
    op.create_index('IDX_depts_is_activate', 'depts', ['is_activate'])
    op.create_index('IDX_depts_created_date', 'depts', ['created_date'])

    # 唯一约束
    op.create_unique_constraint('UNQ_depts_code', 'depts', ['code'])

    # 注：实际项目中，按依赖顺序创建其余 33 张表（略）


def downgrade() -> None:
    """降级：按逆序删除"""
    op.drop_table('depts')
    # 注：实际项目中按逆序逐张 drop（略）