package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

@Data
public class ReleasePageListDto {
    /**
     * 机器人名称
     */
    private String robotName;

    /**
     * 所有者id
     */
    private String creatorId;

    /**
     * 审核状态
     */
    private String status;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 页码
     */
    private Integer pageNo;

    /**
     * 每页大小
     */
    private Integer pageSize;
}
