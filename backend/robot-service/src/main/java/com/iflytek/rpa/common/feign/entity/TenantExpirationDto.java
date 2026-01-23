package com.iflytek.rpa.common.feign.entity;

import lombok.Data;

/**
 * 租户到期信息查询返回DTO
 *
 * @author system
 */
@Data
public class TenantExpirationDto {

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 租户类型（personal-个人版, professional-专业版, enterprise_purchased-买断企业版, enterprise_subscription-非买断企业版）
     */
    private String tenantType;

    /**
     * 到期时间（格式：YYYY-MM-DD）
     * 个人版和买断企业版返回null（不限期）
     */
    private String expirationDate;

    /**
     * 剩余天数
     * 个人版和买断企业版返回null（不限期）
     * 已到期返回负数
     */
    private Long remainingDays;

    /**
     * 是否到期
     * 个人版和买断企业版返回false（不限期）
     */
    private Boolean isExpired;

    /**
     * 是否提示到期（到期前N天需要提醒）
     * 个人版和买断企业版返回false（不限期）
     */
    private Boolean shouldAlert;
}
