-- 多租户资源配置与配额校验系统 - 数据库初始化脚本

-- 1. 创建版本表
CREATE TABLE IF NOT EXISTS `sys_product_version` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `version_code` VARCHAR(50) NOT NULL COMMENT '版本代码（如：personal, professional, enterprise）',
  `deleted` TINYINT(1) DEFAULT 0 COMMENT '删除标识：0-未删除，1-已删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_version_code` (`version_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品版本表';

-- 2. 创建版本默认配置表
CREATE TABLE IF NOT EXISTS `sys_version_default_config` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `version_id` BIGINT(20) NOT NULL COMMENT '版本ID，关联sys_product_version.id',
  `resource_code` VARCHAR(100) NOT NULL COMMENT '资源代码（如：designer_count, component_count等）',
  `resource_type` TINYINT(1) NOT NULL COMMENT '资源类型：1-Quota（配额），2-Switch（开关）',
  `parent_code` VARCHAR(100) DEFAULT NULL COMMENT '父级资源代码（用于层级关系）',
  `default_value` INT(11) NOT NULL COMMENT '默认值（对于Quota是数量，对于Switch是0或1）',
  `url_patterns` TEXT DEFAULT NULL COMMENT 'URL路由模式（JSON数组格式，如：["/api/v1/design/**"]）',
  `description` VARCHAR(500) DEFAULT NULL COMMENT '资源描述',
  `deleted` TINYINT(1) DEFAULT 0 COMMENT '删除标识：0-未删除，1-已删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_version_id` (`version_id`),
  KEY `idx_resource_code` (`resource_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='版本默认配置表';

-- 3. 创建租户配置表
CREATE TABLE IF NOT EXISTS `sys_tenant_config` (
  `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `tenant_id` VARCHAR(64) NOT NULL COMMENT '租户ID',
  `version_id` BIGINT(20) NOT NULL COMMENT '版本ID，关联sys_product_version.id',
  `extra_config_json` TEXT NOT NULL COMMENT '配置快照（JSON格式，只包含type、base、final字段）',
  `deleted` TINYINT(1) DEFAULT 0 COMMENT '删除标识：0-未删除，1-已删除',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tenant_id` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户配置表';

-- 4. 插入版本数据
INSERT INTO `sys_product_version` (`version_code`) VALUES
('personal'),
('professional')
ON DUPLICATE KEY UPDATE `version_code`=VALUES(`version_code`);

-- 5. 插入个人版默认配置
-- 注意：需要先获取个人版的version_id，这里假设为1
SET @personal_version_id = (SELECT id FROM sys_product_version WHERE version_code = 'personal' LIMIT 1);

-- 设计器数量：19个
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@personal_version_id, 'designer_count', 1, 19, '["/robot-design/create", "/robot-design/copy-design-robot", "/market-resource/obtain"]', '设计器数量')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 组件数量：不限（-1表示不限）
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@personal_version_id, 'component_count', 1, -1, '["/api/v1/component/**"]', '组件数量')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 执行器数量：不限
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@personal_version_id, 'executor_count', 1, -1, '["/api/v1/executor/**"]', '执行器数量')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 原子能力：控制台相关隐藏（SWITCH类型，0表示隐藏）
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@personal_version_id, 'atom_console', 2, 0, '["/api/v1/atom/console/**"]', '原子能力-控制台')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 应用市场开关（父级）
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@personal_version_id, 'market_enabled', 2, 1, '["/api/v1/market/**"]', '应用市场开关')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- 应用市场邀请人数：10人
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@personal_version_id, 'market_invite_count', 1, 10, '["/market-user/invite", "/market-invite/generate-invite-link"]', '应用市场邀请人数')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- 应用市场可加入的市场数量：3个
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@personal_version_id, 'market_join_count', 1, 3, '["/market-team/add", "/notify/accept-join-team", "/market-invite/accept-invite"]', '应用市场可加入数量')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- 6. 插入专业版默认配置
SET @professional_version_id = (SELECT id FROM sys_product_version WHERE version_code = 'professional' LIMIT 1);

-- 设计器数量：99个
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@professional_version_id, 'designer_count', 1, 99, '["/robot-design/create", "/robot-design/copy-design-robot", "/market-resource/obtain"]', '设计器数量')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 组件数量：不限
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@professional_version_id, 'component_count', 1, -1, '["/api/v1/component/**"]', '组件数量')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 执行器数量：不限
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@professional_version_id, 'executor_count', 1, -1, '["/api/v1/executor/**"]', '执行器数量')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 原子能力：不做限制（SWITCH类型，1表示启用）
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@professional_version_id, 'atom_console', 2, 1, '["/api/v1/atom/console/**"]', '原子能力-控制台')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- -- 应用市场开关
-- INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
-- (@professional_version_id, 'market_enabled', 2, 1, '["/api/v1/market/**"]', '应用市场开关')
-- ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- 应用市场邀请人数：不限
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@professional_version_id, 'market_invite_count', 1, -1, '["/market-user/invite", "/market-invite/generate-invite-link"]', '应用市场邀请人数')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);

-- 应用市场可加入的市场数量：不限
INSERT INTO `sys_version_default_config` (`version_id`, `resource_code`, `resource_type`, `default_value`, `url_patterns`, `description`) VALUES
(@professional_version_id, 'market_join_count', 1, -1, '["/market-team/add", "/notify/accept-join-team", "/market-invite/accept-invite"]', '应用市场可加入数量')
ON DUPLICATE KEY UPDATE `default_value`=VALUES(`default_value`);