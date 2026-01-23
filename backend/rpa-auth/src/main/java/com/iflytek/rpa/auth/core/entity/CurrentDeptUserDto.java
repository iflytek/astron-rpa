package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-17 16:17
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class CurrentDeptUserDto {
    /**
     * 人员或部门id
     */
    private String id;

    /**
     * 人员或部门名称
     */
    private String name;

    /**
     * 是否置灰
     */
    private Boolean status;

    /**
     * 类型，user:人员，dept:部门
     */
    private String type;

    /**
     * 角色名称
     */
    private String roleName;
}
