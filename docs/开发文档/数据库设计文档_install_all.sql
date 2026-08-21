-- =====================================================================
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

-- ----- depts -----

CREATE TABLE `depts` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '部门名称',
  `code`              VARCHAR(32)     NULL                      COMMENT '部门编码',
  `parent_id`         BIGINT UNSIGNED NULL                      COMMENT '上级部门（自引用）',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '同级排序',
  `leader_id`         BIGINT UNSIGNED NULL                      COMMENT '部门负责人',
  `path`              VARCHAR(255)    NULL                      COMMENT '层级路径（,1,3,7,）',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_depts_code` (`code`),
  KEY `IDX_depts_parent_id` (`parent_id`),
  KEY `IDX_depts_is_activate` (`is_activate`),
  KEY `IDX_depts_created_date` (`created_date`),
  CONSTRAINT `chk_depts_no_self_parent` CHECK (`parent_id` IS NULL OR `parent_id` <> `id`),
  CONSTRAINT `fk_depts_parent` FOREIGN KEY (`parent_id`) REFERENCES `depts` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_depts_leader` FOREIGN KEY (`leader_id`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_depts_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_depts_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表（树形）';;



-- ----- roles -----

CREATE TABLE `roles` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '角色名称',
  `code`              VARCHAR(32)     NOT NULL                  COMMENT '角色代码（唯一）',
  `description`       VARCHAR(255)    NULL                      COMMENT '角色描述',
  `data_scope`        ENUM('ALL','REGION','STORE','SELF') NOT NULL DEFAULT 'REGION' COMMENT '数据范围',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_roles_code` (`code`),
  KEY `IDX_roles_is_activate` (`is_activate`),
  KEY `IDX_roles_created_date` (`created_date`),
  CONSTRAINT `fk_roles_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_roles_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';;



-- ----- permissions -----

CREATE TABLE `permissions` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '权限名称',
  `code`              VARCHAR(64)     NOT NULL                  COMMENT '权限代码（唯一，如 product.create）',
  `module`            VARCHAR(32)     NOT NULL                  COMMENT '所属模块',
  `description`       VARCHAR(255)    NULL                      COMMENT '权限描述',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_permissions_code` (`code`),
  KEY `IDX_permissions_module` (`module`),
  KEY `IDX_permissions_is_activate` (`is_activate`),
  KEY `IDX_permissions_created_date` (`created_date`),
  CONSTRAINT `fk_permissions_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_permissions_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限点';;



-- ----- admin_users -----

CREATE TABLE `admin_users` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username`          VARCHAR(64)     NOT NULL                  COMMENT '登录名（唯一）',
  `password_hash`     VARCHAR(128)    NOT NULL                  COMMENT 'bcrypt 哈希',
  `real_name`         VARCHAR(64)     NULL                      COMMENT '姓名',
  `nickname`          VARCHAR(64)     NULL                      COMMENT '昵称',
  `phone`             VARCHAR(20)     NULL                      COMMENT '手机号',
  `email`             VARCHAR(128)    NULL                      COMMENT '邮箱',
  `gender`            TINYINT         NULL                      COMMENT '0未知 1男 2女',
  `avatar_url`        VARCHAR(255)    NULL                      COMMENT '头像',
  `post`              VARCHAR(64)     NULL                      COMMENT '岗位',
  `dept_id`           BIGINT UNSIGNED NULL                      COMMENT '部门编号',
  `role_id`           BIGINT UNSIGNED NULL                      COMMENT '角色编号（主角色）',
  `failed_attempts`   TINYINT UNSIGNED NOT NULL DEFAULT 0       COMMENT '登录失败次数',
  `locked_until`      DATETIME(3)     NULL                      COMMENT '锁定截止时间',
  `last_login_date`   DATETIME(3)     NULL                      COMMENT '最近登录时间',
  `last_login_ip`     VARCHAR(45)     NULL                      COMMENT '最近登录 IP',
  `data_scope`        ENUM('ALL','REGION','STORE','SELF') NOT NULL DEFAULT 'REGION' COMMENT '数据范围',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_admin_users_username` (`username`),
  KEY `IDX_admin_users_phone` (`phone`),
  KEY `IDX_admin_users_dept_id` (`dept_id`),
  KEY `IDX_admin_users_role_id` (`role_id`),
  KEY `IDX_admin_users_is_activate` (`is_activate`),
  KEY `IDX_admin_users_created_date` (`created_date`),
  CONSTRAINT `chk_admin_users_failed_attempts` CHECK (`failed_attempts` <= 10),
  CONSTRAINT `fk_admin_users_dept` FOREIGN KEY (`dept_id`) REFERENCES `depts` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_users_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_users_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_users_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='后台管理员';;



-- ----- admin_roles -----

CREATE TABLE `admin_roles` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `admin_id`          BIGINT UNSIGNED NOT NULL                  COMMENT '管理员 ID',
  `role_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '角色 ID',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_admin_roles_admin_role` (`admin_id`, `role_id`),
  KEY `IDX_admin_roles_created_date` (`created_date`),
  CONSTRAINT `fk_admin_roles_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_roles_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_roles_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_roles_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员-角色 多对多';;



-- ----- admin_regions -----

CREATE TABLE `admin_regions` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `admin_id`          BIGINT UNSIGNED NOT NULL                  COMMENT '管理员 ID',
  `region_code`       VARCHAR(32)     NOT NULL                  COMMENT '区域代码',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_admin_regions_admin_region` (`admin_id`, `region_code`),
  KEY `IDX_admin_regions_created_date` (`created_date`),
  CONSTRAINT `fk_admin_regions_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_regions_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_admin_regions_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员-区域授权';;



-- ----- role_permissions -----

CREATE TABLE `role_permissions` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `role_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '角色 ID',
  `permission_id`     BIGINT UNSIGNED NOT NULL                  COMMENT '权限 ID',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_role_permissions_role_perm` (`role_id`, `permission_id`),
  KEY `IDX_role_permissions_created_date` (`created_date`),
  CONSTRAINT `fk_role_permissions_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_role_permissions_perm` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_role_permissions_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_role_permissions_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色-权限 关联';;



-- ----- users -----

CREATE TABLE `users` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `phone`             VARCHAR(20)     NOT NULL                  COMMENT '手机号（登录账号）',
  `password_hash`     VARCHAR(128)    NOT NULL                  COMMENT 'bcrypt 哈希',
  `nickname`          VARCHAR(64)     NULL                      COMMENT '昵称',
  `avatar_url`        VARCHAR(255)    NULL                      COMMENT '头像 URL',
  `email`             VARCHAR(128)    NULL                      COMMENT '邮箱',
  `gender`            TINYINT         NULL                      COMMENT '0未知 1男 2女',
  `failed_attempts`   TINYINT UNSIGNED NOT NULL DEFAULT 0       COMMENT '登录失败次数（防爆破）',
  `locked_until`      DATETIME(3)     NULL                      COMMENT '锁定截止时间',
  `last_login_date`   DATETIME(3)     NULL                      COMMENT '最近登录时间',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除时间',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_users_phone` (`phone`),
  KEY `IDX_users_is_activate` (`is_activate`),
  KEY `IDX_users_created_date` (`created_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='前台会员';;



-- ----- user_addresses -----

CREATE TABLE `user_addresses` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '所属会员',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '收货人姓名',
  `phone`             VARCHAR(20)     NOT NULL                  COMMENT '收货人手机号',
  `region_code`       VARCHAR(32)     NULL                      COMMENT '省市区代码',
  `region_name`       VARCHAR(128)    NULL                      COMMENT '省市区文本',
  `address`           VARCHAR(255)    NOT NULL                  COMMENT '详细地址',
  `store_code`        VARCHAR(32)     NULL                      COMMENT '归属门店',
  `is_default`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否默认',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_user_addresses_user_id` (`user_id`),
  KEY `IDX_user_addresses_region_code` (`region_code`),
  KEY `IDX_user_addresses_is_default` (`user_id`, `is_default`),
  KEY `IDX_user_addresses_created_date` (`created_date`),
  CONSTRAINT `fk_user_addresses_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_addresses_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_user_addresses_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会员收货地址';;



-- ----- user_favorites -----

CREATE TABLE `user_favorites` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '会员 ID',
  `product_id`        BIGINT UNSIGNED NOT NULL                  COMMENT '产品 ID',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_user_favorites_user_product` (`user_id`, `product_id`),
  KEY `IDX_user_favorites_product_id` (`product_id`),
  KEY `IDX_user_favorites_created_date` (`created_date`),
  CONSTRAINT `fk_user_favorites_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_favorites_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_user_favorites_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_user_favorites_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会员收藏';;



-- ----- user_search_logs -----

CREATE TABLE `user_search_logs` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '搜索用户（NULL=匿名）',
  `keyword`           VARCHAR(128)    NOT NULL                  COMMENT '搜索关键词',
  `result_count`      INT             NOT NULL DEFAULT 0        COMMENT '结果数',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_user_search_logs_user_id` (`user_id`),
  KEY `IDX_user_search_logs_keyword` (`keyword`),
  KEY `IDX_user_search_logs_created_date` (`created_date`),
  CONSTRAINT `fk_user_search_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_user_search_logs_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_user_search_logs_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='搜索记录';;



-- ----- categories -----

CREATE TABLE `categories` (
  `id`                INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
  `type`              ENUM('series','space','category') NOT NULL  COMMENT '分类类型',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '中文名',
  `name_en`           VARCHAR(64)     NULL                      COMMENT '英文名',
  `icon`              VARCHAR(255)    NULL                      COMMENT '图标 URL',
  `parent_id`         INT UNSIGNED    NULL                      COMMENT '父级 ID（自引用）',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `status`            TINYINT         NOT NULL DEFAULT 1        COMMENT '0禁用 1启用',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_categories_type_status` (`type`, `is_activate`),
  KEY `IDX_categories_parent_id` (`parent_id`),
  KEY `IDX_categories_is_deleted` (`is_deleted`),
  KEY `IDX_categories_created_date` (`created_date`),
  CONSTRAINT `chk_categories_no_self_parent` CHECK (`parent_id` IS NULL OR `parent_id` <> `id`),
  CONSTRAINT `fk_categories_parent` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_categories_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_categories_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品分类字典';;



-- ----- products -----

CREATE TABLE `products` (
  `id`                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product_code`        VARCHAR(64)     NOT NULL                  COMMENT '产品编号（v1.1 新增·唯一）',
  `name`                VARCHAR(128)    NOT NULL                  COMMENT '产品名',
  `subtitle`            VARCHAR(255)    NULL                      COMMENT '副标题',
  `series_id`           INT UNSIGNED    NULL                      COMMENT '所属系列（如胡桃禮，关联 categories.type=series）',
  `space_id`            INT UNSIGNED    NULL                      COMMENT '所属空间分类 id（如客厅/餐厅，关联 categories.type=space）',
  `category_id`         INT UNSIGNED    NULL                      COMMENT '品类（如实木餐桌，关联 categories.type=category）',
  `min_price_cents`     BIGINT          NULL                      COMMENT '最低价（分）',
  `max_price_cents`     BIGINT          NULL                      COMMENT '最高价（分）',
  `cover_url`           VARCHAR(255)    NULL                      COMMENT '封面图片 URL',
  `description`         LONGTEXT        NULL                      COMMENT '产品描述（富文本）',
  `specs_summary`          VARCHAR(500)    NULL                      COMMENT '规格摘要（卡片展示文本）',
  `extra_specs`         JSON            NULL                      COMMENT '规格参数（JSON 串）',
  `other_images_json`   JSON            NULL                      COMMENT '其它图片 URL（JSON 串·v1.1 新增）',
  `support_order`       TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否支持在线下单',
  `sort`                INT             NOT NULL DEFAULT 0        COMMENT '排序值',
  `status`              ENUM('draft','on_sale','off_sale') NOT NULL DEFAULT 'draft' COMMENT '发布状态：草稿/上架/下架（v1.1 改为三态）',
  `is_top`              TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否置顶（v1.1 新增）',
  `is_activate`         TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`          BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`        DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`          BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`        DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`          DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`          TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_products_product_code` (`product_code`) COMMENT '产品编号唯一',
  KEY `IDX_products_category` (`category_id`, `status`, `is_deleted`),
  KEY `IDX_products_series` (`series_id`, `status`, `is_deleted`),
  KEY `IDX_products_space` (`space_id`, `status`, `is_deleted`),
  KEY `IDX_products_support_order` (`support_order`, `status`),
  KEY `IDX_products_status_top` (`status`, `is_top`, `sort`) COMMENT '发布列表（按置顶+排序）',
  KEY `IDX_products_created_date` (`created_date`),
  FULLTEXT KEY `FULLTEXT_products_name` (`name`) WITH PARSER ngram,
  CONSTRAINT `chk_products_category_or_space` CHECK (`category_id` IS NOT NULL OR `space_id` IS NOT NULL OR `series_id` IS NOT NULL),
  CONSTRAINT `chk_products_amount` CHECK (`min_price_cents` IS NULL OR `max_price_cents` IS NULL OR `min_price_cents` <= `max_price_cents`),
  CONSTRAINT `chk_products_draft_no_top` CHECK (NOT (`status` = 'draft' AND `is_top` = 1)) COMMENT '草稿不允许置顶（v1.1 新增）',
  CONSTRAINT `fk_products_series` FOREIGN KEY (`series_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_products_space` FOREIGN KEY (`space_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_products_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_products_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品主表';;



-- ----- product_skus -----

CREATE TABLE `product_skus` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product_id`        BIGINT UNSIGNED NOT NULL                  COMMENT '所属产品',
  `spec_name`         VARCHAR(128)    NOT NULL                  COMMENT '规格名',
  `spec_code`         VARCHAR(64)     NULL                      COMMENT 'SKU 编码',
  `price_cents`       BIGINT          NOT NULL                  COMMENT '价格（分）',
  `stock`             INT             NOT NULL DEFAULT 0        COMMENT '库存',
  `image_url`         VARCHAR(255)    NULL                      COMMENT 'SKU 主图',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_product_skus_code` (`product_id`, `spec_code`),
  KEY `IDX_product_skus_product_id` (`product_id`),
  KEY `IDX_product_skus_created_date` (`created_date`),
  CONSTRAINT `chk_product_skus_price_stock` CHECK (`price_cents` >= 0 AND `stock` >= 0),
  CONSTRAINT `fk_product_skus_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_product_skus_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_product_skus_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品规格';;



-- ----- product_images -----

CREATE TABLE `product_images` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `product_id`        BIGINT UNSIGNED NOT NULL                  COMMENT '所属产品',
  `url`               VARCHAR(255)    NOT NULL                  COMMENT '图片 URL',
  `alt`               VARCHAR(128)    NULL                      COMMENT '替代文本',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_product_images_product_id` (`product_id`, `sort`),
  KEY `IDX_product_images_created_date` (`created_date`),
  CONSTRAINT `fk_product_images_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_product_images_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_product_images_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='产品图片';;



-- ----- banners -----

CREATE TABLE `banners` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '标题',
  `image_url`         VARCHAR(255)    NOT NULL                  COMMENT '图片',
  `link_type`         ENUM('product','news','case','url') NOT NULL DEFAULT 'product' COMMENT '跳转类型',
  `link_target`       VARCHAR(255)    NOT NULL                  COMMENT '跳转目标',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `start_date`        DATETIME(3)     NULL                      COMMENT '上线时间',
  `end_date`          DATETIME(3)     NULL                      COMMENT '下线时间',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_banners_sort` (`sort`),
  KEY `IDX_banners_is_activate` (`is_activate`),
  KEY `IDX_banners_date_range` (`start_date`, `end_date`),
  KEY `IDX_banners_created_date` (`created_date`),
  CONSTRAINT `chk_banners_date_range` CHECK (`start_date` IS NULL OR `end_date` IS NULL OR `start_date` <= `end_date`),
  CONSTRAINT `fk_banners_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_banners_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='首页轮播图';;



-- ----- cases -----

CREATE TABLE `cases` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '案例标题',
  `category_id`       INT UNSIGNED    NULL                      COMMENT '案例分类',
  `cover_url`         VARCHAR(255)    NOT NULL                  COMMENT '封面图',
  `style`             VARCHAR(64)     NULL                      COMMENT '风格',
  `area`              VARCHAR(32)     NULL                      COMMENT '面积',
  `description`       LONGTEXT        NULL                      COMMENT '案例详情',
  `published_date`    DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '发布时间',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `view_count`        INT             NOT NULL DEFAULT 0        COMMENT '浏览量',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_cases_category` (`category_id`, `is_activate`, `is_deleted`),
  KEY `IDX_cases_published` (`published_date`),
  FULLTEXT KEY `FULLTEXT_cases_title` (`title`) WITH PARSER ngram,
  KEY `IDX_cases_created_date` (`created_date`),
  CONSTRAINT `fk_cases_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_cases_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cases_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='案例展示';;



-- ----- case_images -----

CREATE TABLE `case_images` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `case_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '所属案例',
  `url`               VARCHAR(255)    NOT NULL                  COMMENT '图片 URL',
  `caption`           VARCHAR(128)    NULL                      COMMENT '图片说明',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_case_images_case_id` (`case_id`, `sort`),
  KEY `IDX_case_images_created_date` (`created_date`),
  CONSTRAINT `fk_case_images_case` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_case_images_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_case_images_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='案例图集';;



-- ----- news -----

CREATE TABLE `news` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '标题',
  `subtitle`          VARCHAR(255)    NULL                      COMMENT '副标题',
  `category`          ENUM('company','industry') NOT NULL DEFAULT 'company' COMMENT '分类：企业新闻/行业资讯（v1.1 简化为两种）',
  `cover_url`         VARCHAR(255)    NULL                      COMMENT '封面图 URL',
  `summary`           VARCHAR(500)    NULL                      COMMENT '摘要',
  `content`           LONGTEXT        NOT NULL                  COMMENT '正文（富文本 HTML）',
  `author`            VARCHAR(64)     NULL                      COMMENT '作者',
  `source`            VARCHAR(64)     NULL                      COMMENT '来源（转载标注）',
  `view_count`        INT             NOT NULL DEFAULT 0        COMMENT '浏览量',
  `published_date`    DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '发布时间',
  `expire_date`       DATETIME(3)     NULL                      COMMENT '截止时间（NULL=长期有效·v1.1 新增）',
  `is_published`      TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否发布：1已发布 0未发布（v1.1 新增）',
  `is_top`            TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否置顶（v1.1 明确）',
  `is_recommend`      TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '是否推荐：1推荐 0普通（v1.1 新增）',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用（业务状态）',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_news_category` (`category`, `is_activate`, `is_deleted`),
  KEY `IDX_news_published_window` (`is_published`, `published_date`, `expire_date`) COMMENT '按发布状态+时间窗查询（v1.1 调整）',
  KEY `IDX_news_recommend` (`is_recommend`, `is_published`, `published_date`) COMMENT '推荐位（v1.1 新增）',
  FULLTEXT KEY `FULLTEXT_news_title` (`title`) WITH PARSER ngram,
  KEY `IDX_news_created_date` (`created_date`),
  CONSTRAINT `chk_news_publish_window` CHECK (`expire_date` IS NULL OR `expire_date` >= `published_date`) COMMENT '截止时间 ≥ 发布时间（v1.1 新增）',
  CONSTRAINT `chk_news_published_has_date` CHECK (`is_published` = 0 OR `published_date` IS NOT NULL) COMMENT '已发布必须有发布时间（v1.1 新增）',
  CONSTRAINT `fk_news_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_news_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='新闻资讯';;



-- ----- about_sections -----

CREATE TABLE `about_sections` (
  `id`                INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code`              VARCHAR(32)     NOT NULL                  COMMENT '区块代码',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '区块标题',
  `subtitle`          VARCHAR(255)    NULL                      COMMENT '副标题',
  `body`              LONGTEXT        NULL                      COMMENT '富文本正文',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_about_sections_code` (`code`),
  KEY `IDX_about_sections_created_date` (`created_date`),
  CONSTRAINT `fk_about_sections_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_about_sections_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='关于我们区块';;



-- ----- about_images -----

CREATE TABLE `about_images` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `section_id`        INT UNSIGNED    NOT NULL                  COMMENT '所属区块',
  `url`               VARCHAR(255)    NOT NULL                  COMMENT '图片 URL',
  `caption`           VARCHAR(128)    NULL                      COMMENT '图片说明',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_about_images_section_id` (`section_id`, `sort`),
  KEY `IDX_about_images_created_date` (`created_date`),
  CONSTRAINT `fk_about_images_section` FOREIGN KEY (`section_id`) REFERENCES `about_sections` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_about_images_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_about_images_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='关于我们图集';;



-- ----- site_configs -----

CREATE TABLE `site_configs` (
  `id`                INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
  `config_key`        VARCHAR(64)     NOT NULL                  COMMENT '配置键（唯一）',
  `config_value`      TEXT            NOT NULL                  COMMENT '配置值',
  `value_type`        ENUM('string','number','json','bool') NOT NULL DEFAULT 'string' COMMENT '值类型',
  `category`          VARCHAR(32)     NULL                      COMMENT '配置分类',
  `description`       VARCHAR(255)    NULL                      COMMENT '说明',
  `updated_by`        BIGINT UNSIGNED NULL                      COMMENT '最后修改人',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_site_configs_key` (`config_key`),
  KEY `IDX_site_configs_category` (`category`),
  KEY `IDX_site_configs_created_date` (`created_date`),
  CONSTRAINT `fk_site_configs_updated_by` FOREIGN KEY (`updated_by`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_site_configs_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_site_configs_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='站点配置字典';;



-- ----- downloads -----

CREATE TABLE `downloads` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '资料标题',
  `category`          ENUM('catalog','manual','cad','other') NOT NULL DEFAULT 'catalog' COMMENT '资料分类',
  `description`       VARCHAR(500)    NULL                      COMMENT '简介',
  `file_url`          VARCHAR(255)    NOT NULL                  COMMENT '文件 URL',
  `file_size_kb`      INT             NULL                      COMMENT '文件大小 KB',
  `file_format`       VARCHAR(16)     NULL                      COMMENT '文件格式',
  `download_count`    INT             NOT NULL DEFAULT 0        COMMENT '下载次数',
  `sort`              INT             NOT NULL DEFAULT 0        COMMENT '排序',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_downloads_category` (`category`, `is_activate`, `is_deleted`),
  KEY `IDX_downloads_created_date` (`created_date`),
  CONSTRAINT `fk_downloads_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_downloads_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='下载中心';;



-- ----- chat_keywords -----

CREATE TABLE `chat_keywords` (
  `id`                INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
  `keyword`           VARCHAR(64)     NOT NULL                  COMMENT '关键词',
  `reply`             TEXT            NOT NULL                  COMMENT '回复内容',
  `enabled`           TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '是否启用',
  `priority`          INT             NOT NULL DEFAULT 0        COMMENT '优先级（数值大者优先）',
  `match_type`        ENUM('exact','contains','regex') NOT NULL DEFAULT 'exact' COMMENT '匹配方式',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_chat_keywords_enabled_priority` (`enabled`, `is_activate`, `priority`),
  KEY `IDX_chat_keywords_keyword` (`keyword`),
  KEY `IDX_chat_keywords_created_date` (`created_date`),
  CONSTRAINT `fk_chat_keywords_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_chat_keywords_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客服关键词回复';;



-- ----- jobs -----

CREATE TABLE `jobs` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `title`             VARCHAR(128)    NOT NULL                  COMMENT '岗位名称',
  `category`          ENUM('social','campus') NOT NULL DEFAULT 'social' COMMENT '分类',
  `department`        VARCHAR(64)     NULL                      COMMENT '部门',
  `location`          VARCHAR(64)     NULL                      COMMENT '工作地点',
  `salary_min_cents`  BIGINT          NULL                      COMMENT '最低薪资（分）',
  `salary_max_cents`  BIGINT          NULL                      COMMENT '最高薪资（分）',
  `headcount`         INT             NOT NULL DEFAULT 1        COMMENT '招聘人数',
  `description`       LONGTEXT        NULL                      COMMENT '岗位职责',
  `requirement`       LONGTEXT        NULL                      COMMENT '任职要求',
  `publish_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '发布时间',
  `expire_date`       DATETIME(3)     NULL                      COMMENT '截止时间',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  `deleted_at`        DATETIME(3)     NULL                      COMMENT '软删除',
  `is_deleted`        TINYINT(1)      NOT NULL DEFAULT 0        COMMENT '软删除标记',
  PRIMARY KEY (`id`),
  KEY `IDX_jobs_category` (`category`, `is_activate`, `is_deleted`),
  KEY `IDX_jobs_publish` (`publish_date`, `expire_date`),
  KEY `IDX_jobs_created_date` (`created_date`),
  CONSTRAINT `chk_jobs_salary` CHECK (`salary_min_cents` IS NULL OR `salary_max_cents` IS NULL OR `salary_min_cents` <= `salary_max_cents`),
  CONSTRAINT `chk_jobs_date_range` CHECK (`expire_date` IS NULL OR `expire_date` >= `publish_date`),
  CONSTRAINT `fk_jobs_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_jobs_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='招聘岗位';;



-- ----- job_applications -----

CREATE TABLE `job_applications` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `job_id`            BIGINT UNSIGNED NOT NULL                  COMMENT '投递岗位',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '投递人（NULL=匿名）',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '姓名',
  `phone`             VARCHAR(20)     NOT NULL                  COMMENT '手机号',
  `email`             VARCHAR(128)    NULL                      COMMENT '邮箱',
  `resume_url`        VARCHAR(255)    NULL                      COMMENT '简历 URL',
  `region_code`       VARCHAR(32)     NULL                      COMMENT '投递区域',
  `stage`             ENUM('applied','screening','interview','offer','rejected') NOT NULL DEFAULT 'applied' COMMENT '5 阶段状态',
  `reject_reason`     VARCHAR(255)    NULL                      COMMENT '拒绝原因',
  `applied_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '投递时间',
  `screening_date`    DATETIME(3)     NULL                      COMMENT '初筛时间',
  `interview_date`    DATETIME(3)     NULL                      COMMENT '面试时间',
  `offer_date`        DATETIME(3)     NULL                      COMMENT 'Offer 时间',
  `closed_date`       DATETIME(3)     NULL                      COMMENT '终结时间',
  `admin_note`        TEXT            NULL                      COMMENT '内部备注',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_job_applications_job_phone` (`job_id`, `phone`) COMMENT '审核新增：防匿名重复投递',
  KEY `IDX_job_applications_job_id` (`job_id`),
  KEY `IDX_job_applications_user_id` (`user_id`),
  KEY `IDX_job_applications_phone` (`phone`),
  KEY `IDX_job_applications_region_code` (`region_code`),
  KEY `IDX_job_applications_stage` (`stage`, `applied_date`),
  KEY `IDX_job_applications_created_date` (`created_date`),
  CONSTRAINT `chk_job_applications_phone` CHECK (CHAR_LENGTH(`phone`) >= 7),
  CONSTRAINT `fk_job_applications_job` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_job_applications_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_job_applications_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_job_applications_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='投递记录';;



-- ----- appointments -----

CREATE TABLE `appointments` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '预约会员（NULL=匿名）',
  `type`              ENUM('visit','consult','custom','other') NOT NULL DEFAULT 'visit' COMMENT '类型',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '姓名',
  `phone`             VARCHAR(20)     NOT NULL                  COMMENT '手机号',
  `region_code`       VARCHAR(32)     NULL                      COMMENT '客户区域（数据隔离）',
  `store_code`        VARCHAR(32)     NULL                      COMMENT '归属门店（数据隔离）',
  `preferred_date`    DATETIME(3)     NULL                      COMMENT '期望预约时间',
  `message`           TEXT            NULL                      COMMENT '留言',
  `source_page`       VARCHAR(128)    NULL                      COMMENT '来源页面 URL',
  `status`            ENUM('pending','following','converted','invalid') NOT NULL DEFAULT 'pending' COMMENT '跟进状态',
  `assignee_id`       BIGINT UNSIGNED NULL                      COMMENT '跟进人',
  `followed_date`     DATETIME(3)     NULL                      COMMENT '最近跟进时间',
  `follow_note`       TEXT            NULL                      COMMENT '跟进记录',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_appointments_status_date` (`status`, `created_date`),
  KEY `IDX_appointments_region_store` (`region_code`, `store_code`),
  KEY `IDX_appointments_phone` (`phone`),
  KEY `IDX_appointments_user_id` (`user_id`),
  KEY `IDX_appointments_assignee` (`assignee_id`),
  KEY `IDX_appointments_created_date` (`created_date`),
  CONSTRAINT `fk_appointments_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_appointments_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_appointments_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_appointments_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约';;



-- ----- messages -----

CREATE TABLE `messages` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '留言会员（NULL=匿名）',
  `source`            ENUM('chat','job_apply','other') NOT NULL DEFAULT 'chat' COMMENT '来源',
  `ref_id`            BIGINT UNSIGNED NULL                      COMMENT '关联资源 ID',
  `name`              VARCHAR(64)     NOT NULL                  COMMENT '姓名',
  `phone`             VARCHAR(20)     NOT NULL                  COMMENT '手机号',
  `email`             VARCHAR(128)    NULL                      COMMENT '邮箱',
  `region_code`       VARCHAR(32)     NULL                      COMMENT '客户区域',
  `store_code`        VARCHAR(32)     NULL                      COMMENT '归属门店',
  `content`           TEXT            NOT NULL                  COMMENT '留言内容',
  `reply_content`     TEXT            NULL                      COMMENT '客服回复',
  `reply_date`        DATETIME(3)     NULL                      COMMENT '回复时间',
  `reply_by`          BIGINT UNSIGNED NULL                      COMMENT '回复人',
  `status`            ENUM('pending','replied','closed') NOT NULL DEFAULT 'pending' COMMENT '状态',
  `assignee_id`       BIGINT UNSIGNED NULL                      COMMENT '处理人',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_messages_source_status` (`source`, `status`, `created_date`),
  KEY `IDX_messages_region_store` (`region_code`, `store_code`),
  KEY `IDX_messages_user_id` (`user_id`),
  KEY `IDX_messages_assignee` (`assignee_id`),
  KEY `IDX_messages_reply_by` (`reply_by`),
  KEY `IDX_messages_created_date` (`created_date`),
  CONSTRAINT `fk_messages_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_assignee` FOREIGN KEY (`assignee_id`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_reply_by` FOREIGN KEY (`reply_by`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_messages_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='留言';;



-- ----- cart_items -----

CREATE TABLE `cart_items` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NOT NULL                  COMMENT '会员',
  `sku_id`            BIGINT UNSIGNED NOT NULL                  COMMENT 'SKU',
  `quantity`          INT             NOT NULL DEFAULT 1        COMMENT '数量',
  `selected`          TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '结算选中',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_cart_items_user_sku` (`user_id`, `sku_id`),
  KEY `IDX_cart_items_created_date` (`created_date`),
  CONSTRAINT `chk_cart_items_quantity` CHECK (`quantity` > 0 AND `quantity` <= 999),
  CONSTRAINT `fk_cart_items_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_items_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_items_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_items_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车';;



-- ----- orders -----

CREATE TABLE `orders` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `order_no`          VARCHAR(32)     NOT NULL                  COMMENT '订单号（唯一）',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '下单人（NULL=游客）',
  `address_id`        BIGINT UNSIGNED NULL                      COMMENT '收货地址 ID',
  `receiver_name`     VARCHAR(64)     NULL                      COMMENT '收货人姓名（快照）',
  `receiver_phone`    VARCHAR(20)     NULL                      COMMENT '收货人手机（快照）',
  `receiver_address`  VARCHAR(255)    NULL                      COMMENT '收货地址文本（快照）',
  `region_code`       VARCHAR(32)     NULL                      COMMENT '收货区域',
  `store_code`        VARCHAR(32)     NULL                      COMMENT '归属门店',
  `status`            ENUM('pending','paid','shipped','completed','refunding','refunded','closed') NOT NULL DEFAULT 'pending' COMMENT '订单状态',
  `total_cents`       BIGINT          NOT NULL                  COMMENT '商品总额（分）',
  `shipping_cents`    BIGINT          NOT NULL DEFAULT 0        COMMENT '运费（分）',
  `discount_cents`    BIGINT          NOT NULL DEFAULT 0        COMMENT '优惠（分·二期预留）',
  `final_cents`       BIGINT          NOT NULL                  COMMENT '实付金额（分）',
  `remark`            VARCHAR(500)    NULL                      COMMENT '用户备注',
  `paid_date`         DATETIME(3)     NULL                      COMMENT '支付时间',
  `shipped_date`      DATETIME(3)     NULL                      COMMENT '发货时间',
  `completed_date`    DATETIME(3)     NULL                      COMMENT '完成时间',
  `closed_date`       DATETIME(3)     NULL                      COMMENT '关闭时间',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_orders_order_no` (`order_no`),
  KEY `IDX_orders_user_status` (`user_id`, `status`, `created_date`),
  KEY `IDX_orders_status_date` (`status`, `created_date`),
  KEY `IDX_orders_region_store` (`region_code`, `store_code`),
  KEY `IDX_orders_final_cents` (`final_cents`),
  KEY `IDX_orders_created_date` (`created_date`),
  CONSTRAINT `chk_orders_amount` CHECK (
    `total_cents` >= 0 AND `shipping_cents` >= 0 AND `discount_cents` >= 0 AND
    `final_cents` = `total_cents` + `shipping_cents` - `discount_cents`
  ),
  CONSTRAINT `chk_orders_status_timeline` CHECK (
    (`paid_date` IS NULL OR `paid_date` >= `created_date`) AND
    (`shipped_date` IS NULL OR `shipped_date` >= COALESCE(`paid_date`, `created_date`)) AND
    (`completed_date` IS NULL OR `completed_date` >= COALESCE(`shipped_date`, `created_date`))
  ),
  CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_address` FOREIGN KEY (`address_id`) REFERENCES `user_addresses` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单主表';;



-- ----- order_items -----

CREATE TABLE `order_items` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `order_id`          BIGINT UNSIGNED NOT NULL                  COMMENT '所属订单',
  `product_id`        BIGINT UNSIGNED NOT NULL                  COMMENT '产品 ID',
  `sku_id`            BIGINT UNSIGNED NULL                      COMMENT 'SKU ID',
  `product_name`      VARCHAR(128)    NOT NULL                  COMMENT '产品名（快照）',
  `sku_name`          VARCHAR(128)    NULL                      COMMENT 'SKU 名（快照）',
  `price_cents`       BIGINT          NOT NULL                  COMMENT '单价（快照·分）',
  `quantity`          INT             NOT NULL                  COMMENT '数量',
  `subtotal_cents`    BIGINT          NOT NULL                  COMMENT '小计（分）',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_order_items_order_id` (`order_id`),
  KEY `IDX_order_items_product_id` (`product_id`),
  KEY `IDX_order_items_sku_id` (`sku_id`),
  KEY `IDX_order_items_created_date` (`created_date`),
  CONSTRAINT `chk_order_items_amount` CHECK (`subtotal_cents` = `price_cents` * `quantity` AND `quantity` > 0 AND `price_cents` >= 0),
  CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_sku` FOREIGN KEY (`sku_id`) REFERENCES `product_skus` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细';;



-- ----- payments -----

CREATE TABLE `payments` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `order_id`          BIGINT UNSIGNED NOT NULL                  COMMENT '所属订单',
  `channel`           ENUM('wechat','alipay','offline') NOT NULL DEFAULT 'wechat' COMMENT '支付渠道（二期）',
  `transaction_id`    VARCHAR(128)    NULL                      COMMENT '第三方交易号',
  `amount_cents`      BIGINT          NOT NULL                  COMMENT '支付金额（分）',
  `status`            ENUM('pending','success','failed','refunded') NOT NULL DEFAULT 'pending' COMMENT '支付状态',
  `paid_date`         DATETIME(3)     NULL                      COMMENT '支付完成时间',
  `raw_response`      JSON            NULL                      COMMENT '第三方返回原始数据',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNQ_payments_transaction` (`transaction_id`),
  KEY `IDX_payments_order_id` (`order_id`),
  KEY `IDX_payments_status_date` (`status`, `paid_date`),
  KEY `IDX_payments_created_date` (`created_date`),
  CONSTRAINT `chk_payments_amount` CHECK (`amount_cents` >= 0),
  CONSTRAINT `fk_payments_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='支付记录（二期）';;



-- ----- stats_visit -----

CREATE TABLE `stats_visit` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id`           BIGINT UNSIGNED NULL                      COMMENT '访问用户（NULL=游客）',
  `path`              VARCHAR(255)    NOT NULL                  COMMENT '访问路径',
  `referer`           VARCHAR(255)    NULL                      COMMENT '来源页面',
  `ip`                VARCHAR(45)     NULL                      COMMENT '访问 IP',
  `user_agent`        VARCHAR(255)    NULL                      COMMENT '浏览器 UA',
  `device_type`       ENUM('desktop','mobile','tablet') NULL    COMMENT '设备类型',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_stats_visit_user_id` (`user_id`),
  KEY `IDX_stats_visit_path` (`path`),
  KEY `IDX_stats_visit_created_date` (`created_date`),
  CONSTRAINT `fk_stats_visit_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_stats_visit_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_stats_visit_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='访问日志';;



-- ----- audit_logs -----

CREATE TABLE `audit_logs` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `admin_id`          BIGINT UNSIGNED NULL                      COMMENT '操作人',
  `action`            VARCHAR(64)     NOT NULL                  COMMENT '操作类型（如 product.create）',
  `resource`          VARCHAR(32)     NOT NULL                  COMMENT '资源类型',
  `resource_id`       BIGINT UNSIGNED NULL                      COMMENT '资源 ID',
  `payload`           JSON            NULL                      COMMENT '变更详情（脱敏）',
  `ip`                VARCHAR(45)     NULL                      COMMENT '操作 IP',
  `user_agent`        VARCHAR(255)    NULL                      COMMENT '浏览器 UA',
  `is_activate`       TINYINT(1)      NOT NULL DEFAULT 1        COMMENT '激活/禁用',
  `created_at`        BIGINT UNSIGNED NULL                      COMMENT '创建人',
  `created_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at`        BIGINT UNSIGNED NULL                      COMMENT '修改人',
  `updated_date`      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `IDX_audit_logs_admin_id` (`admin_id`),
  KEY `IDX_audit_logs_resource` (`resource`, `resource_id`),
  KEY `IDX_audit_logs_action` (`action`),
  KEY `IDX_audit_logs_created_date` (`created_date`),
  CONSTRAINT `fk_audit_logs_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_audit_logs_created_at` FOREIGN KEY (`created_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_audit_logs_updated_at` FOREIGN KEY (`updated_at`) REFERENCES `admin_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作审计日志';;



-- =====================================================================
-- 第 2 部分：触发器
-- =====================================================================

DELIMITER $$

CREATE TRIGGER `trg_order_items_after_insert`
AFTER INSERT ON `order_items`
FOR EACH ROW
BEGIN
  UPDATE `orders`
    SET `total_cents` = (
      SELECT IFNULL(SUM(`subtotal_cents`), 0)
      FROM `order_items`
      WHERE `order_id` = NEW.`order_id`
    )
    WHERE `id` = NEW.`order_id`;
END$$

CREATE TRIGGER `trg_order_items_after_update`
AFTER UPDATE ON `order_items`
FOR EACH ROW
BEGIN
  UPDATE `orders`
    SET `total_cents` = (
      SELECT IFNULL(SUM(`subtotal_cents`), 0)
      FROM `order_items`
      WHERE `order_id` = NEW.`order_id`
    )
    WHERE `id` = NEW.`order_id`;
END$$

CREATE TRIGGER `trg_order_items_after_delete`
AFTER DELETE ON `order_items`
FOR EACH ROW
BEGIN
  UPDATE `orders`
    SET `total_cents` = (
      SELECT IFNULL(SUM(`subtotal_cents`), 0)
      FROM `order_items`
      WHERE `order_id` = OLD.`order_id`
    )
    WHERE `id` = OLD.`order_id`;
END$$

DELIMITER ;

-- =====================================================================
-- 第 3 部分：视图
-- =====================================================================

CREATE OR REPLACE VIEW `v_member_summary` AS
SELECT
  u.`id`,
  u.`phone`,
  u.`nickname`,
  u.`avatar_url`,
  u.`email`,
  u.`gender`,
  u.`is_activate`,
  u.`last_login_date`,
  u.`created_date`,
  COUNT(DISTINCT a.`id`) AS `address_count`,
  COUNT(DISTINCT f.`id`) AS `favorite_count`,
  COUNT(DISTINCT o.`id`) AS `order_count`,
  COALESCE(SUM(o.`final_cents`), 0) AS `total_spent_cents`
FROM `users` u
LEFT JOIN `user_addresses` a ON a.`user_id` = u.`id` AND a.`is_activate` = 1
LEFT JOIN `user_favorites` f ON f.`user_id` = u.`id` AND f.`is_activate` = 1
LEFT JOIN `orders` o ON o.`user_id` = u.`id`
WHERE u.`is_deleted` = 0
GROUP BY u.`id`;

CREATE OR REPLACE VIEW `v_order_detail` AS
SELECT
  o.`id` AS `order_id`,
  o.`order_no`,
  o.`status`,
  o.`final_cents`,
  o.`region_code`,
  o.`store_code`,
  o.`created_date`,
  o.`paid_date`,
  o.`shipped_date`,
  o.`completed_date`,
  o.`receiver_name`,
  o.`receiver_phone`,
  u.`phone` AS `user_phone`,
  COUNT(DISTINCT oi.`id`) AS `item_count`,
  SUM(oi.`quantity`) AS `total_quantity`
FROM `orders` o
LEFT JOIN `users` u ON u.`id` = o.`user_id`
LEFT JOIN `order_items` oi ON oi.`order_id` = o.`id`
GROUP BY o.`id`;

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
