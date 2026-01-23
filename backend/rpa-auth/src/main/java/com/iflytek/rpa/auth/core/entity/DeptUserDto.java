package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-06 19:08
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class DeptUserDto extends User {

    private String roleId;

    private String roleName;
}
