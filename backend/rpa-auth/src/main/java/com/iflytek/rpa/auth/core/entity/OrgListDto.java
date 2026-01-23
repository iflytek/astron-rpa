package com.iflytek.rpa.auth.core.entity;

import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-11 15:40
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class OrgListDto extends PageQueryDto {

    private List<String> orgIds;

    private String orgName;
}
