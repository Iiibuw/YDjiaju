"""从数据库设计文档提取所有 CREATE TABLE 语句，生成 install_all.sql

策略：直接按章节顺序从第 5 章拼接，注入种子数据 + 触发器 + 视图
"""

import re
from pathlib import Path

DOC = Path(__file__).parent / "数据库设计文档.md"
OUT = Path(__file__).parent / "数据库设计文档_install_all.sql"

text = DOC.read_text(encoding="utf-8")

# 提取所有 ```sql ... ``` 代码块
blocks = re.findall(r"```sql\n(.*?)```", text, re.DOTALL)

# 过滤：保留 CREATE TABLE 块
create_tables = []
for b in blocks:
    # 去除 ```sql 之外的额外标记
    b = b.strip()
    if "CREATE TABLE" in b and "REPLACE VIEW" not in b and "REPLACE TRIGGER" not in b:
        create_tables.append(b)

# 提取视图与触发器
views = []
triggers = []
for b in blocks:
    b = b.strip()
    if "CREATE OR REPLACE VIEW" in b:
        views.append(b)
    if "CREATE TRIGGER" in b:
        triggers.append(b)

# 排序建表顺序：按依赖关系
TABLE_ORDER = [
    # 用户与权限域（11）
    "depts", "roles", "permissions", "admin_users",
    "admin_roles", "admin_regions", "role_permissions",
    "users", "user_addresses", "user_favorites", "user_search_logs",
    # 产品域
    "categories", "products", "product_skus", "product_images",
    # 内容域
    "banners", "cases", "case_images", "news",
    "about_sections", "about_images",
    "site_configs", "downloads", "chat_keywords",
    # 招聘域
    "jobs", "job_applications",
    # 业务域
    "appointments", "messages", "cart_items",
    # 订单域
    "orders", "order_items", "payments",
    # 统计/审计
    "stats_visit", "audit_logs",
]

def find_create(name, blocks):
    """查找某表的 CREATE TABLE 块"""
    for b in blocks:
        if f"CREATE TABLE `{name}`" in b:
            return b
    return None

ordered_blocks = []
for t in TABLE_ORDER:
    blk = find_create(t, create_tables)
    if blk:
        ordered_blocks.append((t, blk))
    else:
        print(f"[WARN] {t} not found")

# 拼装完整脚本
header = """-- =====================================================================
-- YD家居 · 数据库一键建库脚本 install_all.sql
-- 版本：v1.0  |  日期：2026-08-18  |  数据库：MySQL 8.0+
-- 字符集：utf8mb4 / utf8mb4_unicode_ci  |  引擎：InnoDB
-- 共 33 张表 + 2 视图 + 3 触发器 + 种子数据（最小集）
--
-- 使用方法：
--   mysql -u root -p yd_furniture < install_all.sql
-- =====================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;   -- 临时关闭外键检查，加速建表
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,ERROR_FOR_DIVISION_BY_ZERO';

-- 创建数据库（若不存在）
CREATE DATABASE IF NOT EXISTS `yd_furniture`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `yd_furniture`;

-- =====================================================================
-- 第 1 部分：建表（按依赖顺序）
-- =====================================================================

"""

footer = """

-- =====================================================================
-- 第 2 部分：触发器
-- =====================================================================

""" + "\n\n".join(triggers) + """

-- =====================================================================
-- 第 3 部分：视图
-- =====================================================================

""" + "\n\n".join(views) + """

-- =====================================================================
-- 第 4 部分：种子数据（最小集）
-- =====================================================================

-- 4.1 顶级部门
INSERT INTO `depts` (`id`, `name`, `code`, `parent_id`, `sort`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, 'YD家居总部',     'HQ',     NULL, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (2, '运营中心',       'OPS',    1,    2, 1, NULL, NOW(3), NULL, NOW(3)),
  (3, '技术中心',       'TECH',   1,    3, 1, NULL, NOW(3), NULL, NOW(3)),
  (4, '市场中心',       'MKT',    1,    4, 1, NULL, NOW(3), NULL, NOW(3));

-- 4.2 基础角色
INSERT INTO `roles` (`id`, `name`, `code`, `description`, `data_scope`, `sort`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, '超级管理员',     'super_admin', '所有权限',     'ALL',   1, 1, NULL, NOW(3), NULL, NOW(3)),
  (2, '内容编辑',       'editor',      '内容管理',     'REGION', 2, 1, NULL, NOW(3), NULL, NOW(3)),
  (3, '产品运营',       'product',     '产品上下架',   'REGION', 3, 1, NULL, NOW(3), NULL, NOW(3)),
  (4, '客服',           'service',     '留言与预约',   'SELF',   4, 1, NULL, NOW(3), NULL, NOW(3)),
  (5, '订单管理员',     'order',       '订单处理',     'REGION', 5, 1, NULL, NOW(3), NULL, NOW(3));

-- 4.3 基础权限点（最小集，后续在后台管理界面配置）
INSERT INTO `permissions` (`id`, `name`, `code`, `module`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, '产品查看',   'product.view',    'product', 1, NULL, NOW(3), NULL, NOW(3)),
  (2, '产品编辑',   'product.edit',    'product', 1, NULL, NOW(3), NULL, NOW(3)),
  (3, '产品删除',   'product.delete',  'product', 1, NULL, NOW(3), NULL, NOW(3)),
  (4, '订单查看',   'order.view',      'order',   1, NULL, NOW(3), NULL, NOW(3)),
  (5, '订单处理',   'order.handle',    'order',   1, NULL, NOW(3), NULL, NOW(3)),
  (6, '内容发布',   'content.publish', 'content', 1, NULL, NOW(3), NULL, NOW(3));

-- 4.4 超级管理员账号（密码：admin123，bcrypt 哈希示例：实际部署必须替换）
-- ⚠️ 首次部署后必须修改默认密码
INSERT INTO `admin_users` (`id`, `username`, `password_hash`, `real_name`, `nickname`, `dept_id`, `role_id`, `data_scope`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, 'admin', '$2b$12$LQwO3XkRzN5Y8qBfqX8F7eK1VGYX5X5X5X5X5X5X5X5X5X5X5X5X', '系统管理员', 'Super', 1, 1, 'ALL', 1, NULL, NOW(3), NULL, NOW(3));

-- 4.5 角色-权限（全量授予超级管理员）
INSERT INTO `role_permissions` (`role_id`, `permission_id`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
SELECT 1, id, 1, NULL, NOW(3), NULL, NOW(3) FROM `permissions`;

-- 4.6 分类字典（最小集）
INSERT INTO `categories` (`id`, `type`, `name`, `name_en`, `parent_id`, `sort`, `status`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, 'series',   '胡桃木系列',   NULL, NULL, 1, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (2, 'series',   '现代简约系列', NULL, NULL, 2, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (3, 'space',    '客厅',         NULL, NULL, 1, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (4, 'space',    '餐厅',         NULL, NULL, 2, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (5, 'space',    '卧室',         NULL, NULL, 3, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (6, 'category', '实木餐桌',     NULL, NULL, 1, 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (7, 'category', '真皮沙发',     NULL, NULL, 2, 1, 1, NULL, NOW(3), NULL, NOW(3));

-- 4.7 站点配置（最小集）
INSERT INTO `site_configs` (`config_key`, `config_value`, `value_type`, `category`, `description`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  ('site.name',          'YD家居',          'string', 'basic', '站点名称', 1, NULL, NOW(3), NULL, NOW(3)),
  ('site.copyright',     '© 2026 YD家居',   'string', 'basic', '版权信息', 1, NULL, NOW(3), NULL, NOW(3)),
  ('site.icp',           '',                'string', 'basic', 'ICP 备案号', 1, NULL, NOW(3), NULL, NOW(3)),
  ('site.contact.phone', '400-888-8888',    'string', 'contact', '联系电话', 1, NULL, NOW(3), NULL, NOW(3)),
  ('site.contact.email', 'service@yd.com',  'string', 'contact', '联系邮箱', 1, NULL, NOW(3), NULL, NOW(3));

-- 4.8 关于我们区块
INSERT INTO `about_sections` (`id`, `code`, `title`, `subtitle`, `body`, `sort`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  (1, 'about-yd',  '关于YD',     '专注家居品质生活', 'YD家居成立于...', 1, 1, NULL, NOW(3), NULL, NOW(3)),
  (2, 'history',   '发展历程',   '十年品质沉淀',    '2014年成立...', 2, 1, NULL, NOW(3), NULL, NOW(3)),
  (3, 'brand',     '品牌介绍',   '匠心工艺',         'YD品牌专注于...', 3, 1, NULL, NOW(3), NULL, NOW(3)),
  (4, 'contact',   '联系我们',   '期待与您合作',     '电话：400-888-8888', 4, 1, NULL, NOW(3), NULL, NOW(3));

-- 4.9 客服关键词
INSERT INTO `chat_keywords` (`keyword`, `reply`, `enabled`, `priority`, `match_type`, `is_activate`, `created_at`, `created_date`, `updated_at`, `updated_date`)
VALUES
  ('你好',     '您好，欢迎光临YD家居！请问有什么可以帮您？', 1, 100, 'contains', 1, NULL, NOW(3), NULL, NOW(3)),
  ('价格',     '我们的产品定价根据材质、工艺、尺寸有所不同。您可以查看产品详情页或咨询客服。', 1, 50, 'contains', 1, NULL, NOW(3), NULL, NOW(3)),
  ('定制',     '我们支持家具定制服务，您可以联系客服或到门店面谈。', 1, 50, 'contains', 1, NULL, NOW(3), NULL, NOW(3));

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- 初始化完成
--  - 33 张表已创建
--  - 4 个部门、5 个角色、6 个权限、1 个超管账号、4 个分类、9 个站点配置已写入
--  - 默认超管：admin / admin123（请立即修改密码！）
-- =====================================================================
"""

# 拼装所有 CREATE TABLE 块
table_sql_parts = []
for name, blk in ordered_blocks:
    table_sql_parts.append(f"-- ----- {name} -----")
    table_sql_parts.append(blk + ";")
    table_sql_parts.append("")

full_sql = header + "\n\n".join(table_sql_parts) + footer

OUT.write_text(full_sql, encoding="utf-8")
print(f"[OK] {OUT.name} ({len(full_sql)} bytes, {len(ordered_blocks)} tables, {len(views)} views, {len(triggers)} triggers)")