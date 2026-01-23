package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class UsePermissionCheckDto {
    /**
     * 应用ID（必填）
     */
    @NotBlank(message = "应用ID不能为空")
    private String appId;

    /**
     * 市场ID（必填）
     */
    @NotBlank(message = "市场ID不能为空")
    private String marketId;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 租户ID
     */
    private String tenantId;
} 