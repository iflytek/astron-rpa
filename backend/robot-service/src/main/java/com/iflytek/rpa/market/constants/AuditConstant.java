package com.iflytek.rpa.market.constants;

/**
 * @author mjren
 * @date 2025-07-02 11:19
 * @copyright Copyright (c) 2025 mjren
 */
public class AuditConstant {
    /**
     * 状态: 待审核pending, 已通过approved, 未通过rejected, 已撤销canceled
     */
    public static final String AUDIT_STATUS_PENDING = "pending";

    public static final String AUDIT_STATUS_APPROVED = "approved";

    public static final String AUDIT_STATUS_REJECTED = "rejected";

    public static final String AUDIT_STATUS_CANCELED = "canceled";

    public static final String AUDIT_STATUS_NULLIFY = "nullify";

    /**
     * 审核开关状态
     */
    public static final Short AUDIT_ENABLE_ON = 1; // 启用审核

    public static final Short AUDIT_ENABLE_OFF = 0; // 禁用审核

    /**
     * 审核开关状态字符串
     */
    public static final String AUDIT_ENABLE_STATUS_ON = "on"; // 启用

    public static final String AUDIT_ENABLE_STATUS_OFF = "off"; // 禁用
}
