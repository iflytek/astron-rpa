package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

/**
 * 卓越中心上架审核列表查询DTO
 */
@Data
public class ReleaseAuditListDto extends ReleasePageListDto {

    /**
     * 密级筛选：red, yellow, green
     */
    private String securityLevel;

    /**
     * 申请状态筛选
     */
    private String applicationStatus;

    /**
     * 租户ID筛选
     */
    private String tenantId;
}
