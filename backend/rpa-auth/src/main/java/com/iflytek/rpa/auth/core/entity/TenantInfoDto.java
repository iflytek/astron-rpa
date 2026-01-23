package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-19 10:28
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class TenantInfoDto {
    /**
     * 租户id
     */
    private String id;

    /**
     * 租户名称
     */
    private String name;

    /**
     * 租户编码
     */
    private String code;

    /**
     * 管理员id
     */
    private String managerId;

    /**
     * 管理员名称
     */
    private String managerName;
}
