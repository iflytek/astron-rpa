package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.NotNull;
import java.util.List;

/**
 * 卓越中心版本推送DTO
 */
@Data
public class ExcellencePushDto {

    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    @NotNull(message = "机器人版本不能为空")
    private Integer robotVersion;

    /**
     * 目标租户ID列表
     */
    @NotEmpty(message = "目标用户列表不能为空")
    private List<String> userIdList;

    /**
     * 推送策略：auto(自动推送), manual(手动确认)
     */
    private String pushStrategy;

    /**
     * 密级控制：是否仅推送给符合密级要求的租户
     */
    private Boolean securityControl;

    /**
     * 推送说明
     */
    private String pushDescription;
} 