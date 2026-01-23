package com.iflytek.rpa.auth.core.entity;

import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-17 20:35
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class BindUserListDto {

    private String roleId;

    private List<String> userIds;
}
