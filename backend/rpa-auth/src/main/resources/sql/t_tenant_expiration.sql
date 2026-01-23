-- 租户到期信息表
CREATE TABLE IF NOT EXISTS `t_tenant_expiration` (
  `id` VARCHAR(64) NOT NULL COMMENT '主键ID',
  `tenant_id` VARCHAR(64) NOT NULL COMMENT '租户ID',
  `expiration_date` VARCHAR(64) DEFAULT NULL COMMENT '到期时间（格式：YYYY-MM-DD，非买断企业版为加密数据，专业版为明文）',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_delete` TINYINT(1) DEFAULT 0 COMMENT '是否删除（0-否，1-是）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_tenant_id` (`tenant_id`),
  KEY `idx_tenant_id` (`tenant_id`),
  KEY `idx_is_delete` (`is_delete`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='租户到期信息表';

