package com.iflytek.rpa.base.entity.dto;

import java.io.Serializable;
import java.util.Map;
import lombok.Data;

/**
 * 租户配置Map DTO
 * 用于存储完整的租户配置JSON结构
 * {
 *   "resource_code": ResourceConfigDto
 * }
 */
@Data
public class TenantConfigMapDto implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 资源代码到配置的映射
     */
    private Map<String, ResourceConfigDto> configs;
}
