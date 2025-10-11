package com.iflytek.rpa.market.entity.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-02 15:33
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class ChangeAuditDto {

    @NotNull(message = "id不能为空")
    private Long id;

    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    /**
     * 变更后的密级red,green,yellow
     */
    private String securityLevel;

    /**
     * 允许使用的部门ID列表
     */
    private String allowedDept;

    /**
     * 选择绿色密级时，后续更新发版是否默认通过
     */
    private Integer defaultPass;
}
