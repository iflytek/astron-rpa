package com.iflytek.rpa.market.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-01 10:16
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class AppApplicationTenant {
    private String tenantId;
    private Short auditEnable;

    /**
     * 审核开关状态变更时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date auditEnableTime;

    /**
     * 审核开关状态变更操作人
     */
    private String auditEnableOperator;

    /**
     * 审核开关状态变更原因
     */
    private String auditEnableReason;
}
