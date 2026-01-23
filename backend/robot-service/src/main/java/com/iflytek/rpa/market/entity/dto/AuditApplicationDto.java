package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

/**
 * @author mjren
 * @date 2025-07-02 9:44
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class AuditApplicationDto {

    private String id;

    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    @NotNull(message = "机器人版本不能为空")
    private Long robotVersion;

    /**
     * 申请类型: release(上架)/use(使用)
     */
    @NotBlank(message = "申请类型不能为空")
    private String applicationType;

    /**
     * 状态: 待审核pending, 已通过approved, 未通过rejected, 已撤销canceled
     */
    @NotBlank(message = "审核结果不能为空")
    private String status;


    /**
     * 审核设置的密级red,green,yellow
     */
    private String securityLevel;

    /**
     * 允许使用的部门ID列表
     */
    private String allowedDept;

    /**
     * 使用期限(week,month,quarter)
     */
    private String expireTime;

    /**
     * 审核意见
     */
    private String auditOpinion;


    /**
     * 选择绿色密级时，后续更新发版是否默认通过
     */
    private Short defaultPass;


}
