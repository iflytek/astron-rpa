package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * 用户角色信息DTO
 * @author system
 * @date 2025-01-27
 */
@Data
public class UserRoleDto {
    /**
     * 用户ID
     */
    private String userId;

    /**
     * 角色名称
     */
    private String roleName;
}
