package com.iflytek.rpa.auth.core.entity;

import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-05 16:50
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class BindResourceDto {

    private String tenantId;

    private String roleId;

    private List<String> resourceIds;

    private String authId;
}
