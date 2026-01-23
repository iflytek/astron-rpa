package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-05-27 15:52
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class UserSearchDto {

    /**
     * 用户id
     */
    private String id;

    /**
     * 姓名
     */
    private String name;

    private String phone;
}
