package com.iflytek.rpa.auth.core.entity;

import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-28 15:33
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class UserChangeDeptDto {

    private List<UpdateUserDto> userList;

    private String deptId;
}
