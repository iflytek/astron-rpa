package com.iflytek.rpa.auth.core.entity;

import lombok.Data;

import java.util.List;

/**
 * @author mjren
 * @date 2025-03-13 14:47
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class GetDeptOrUserDto {

    private List<User> userList;

    private List<Org> deptList;

}
