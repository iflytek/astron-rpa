package com.iflytek.rpa.auth.sp.uap.constants;

public class UAPConstant {
    public static final String PERSONAL_TENANT_CODE = "pe_";

    /**
     * 专业版租户前缀
     */
    public static final String PROFESSIONAL_TENANT_CODE = "pr_";

    /**
     * 买断企业版租户前缀
     */
    public static final String ENTERPRISE_PURCHASED_TENANT_CODE = "ep_";

    /**
     * 非买断企业版租户前缀
     */
    public static final String ENTERPRISE_SUBSCRIPTION_TENANT_CODE = "es_";

    /**
     * 租户类型：个人版
     */
    public static final String TENANT_TYPE_PERSONAL = "personal";

    /**
     * 租户类型：专业版
     */
    public static final String TENANT_TYPE_PROFESSIONAL = "professional";

    /**
     * 租户类型：买断企业版
     */
    public static final String TENANT_TYPE_ENTERPRISE_PURCHASED = "enterprise_purchased";

    /**
     * 租户类型：非买断企业版
     */
    public static final String TENANT_TYPE_ENTERPRISE_SUBSCRIPTION = "enterprise_subscription";

    public static final String RPA_CLIENT_NAME = "RPA客户端";

    public static final String RPA_ADMIN_NAME = "卓越中心";

    public static final String DEFAULT_INITIAL_PASSWORD = "y3#J3vm!4hJ8k2v";

    /**
     * 登录平台：客户端
     */
    public static final String PLATFORM_CLIENT = "client";

    /**
     * 登录平台：运营后台
     */
    public static final String PLATFORM_ADMIN = "admin";

    /**
     * 登录平台：邀请链接
     */
    public static final String PLATFORM_INVITE = "invite";

    /**
     * Session中存储platform的key
     */
    public static final String SESSION_KEY_PLATFORM = "login_platform";
}
