package com.iflytek.rpa.auth.sp.uap.constants;

public class RedisKeyConstant {
    public static final String REDIS_KEY_DEPT_CHILD_NODES_PREFIX = "dept:childrenNodes:";

    public static final String REDIS_KEY_DEPT_PERSON_CHILD_NODES_PREFIX = "dept:person:childrenNodes:";

    public static final String REDIS_KEY_DEPT_ALL_USER_PREFIX = "dept:user:user_name:";

    public static final String REDIS_KEY_DEPT_PREFIX = "dept:";

    public static final String REDIS_KEY_DEPT_USER_PREFIX = "dept:user:";

    public static final String REDIS_KEY_TENANT_USER_PREFIX = "tenant:user:";

    /**
     * 用户session映射前缀
     * Key格式: user:session:{userId}
     * Value: sessionId
     */
    public static final String REDIS_KEY_USER_SESSION_PREFIX = "user:session:";

    /**
     * 租户空间拥有状态前缀
     * Key格式: tenant:has_space:{tenantId}
     * Value: "true" 或 "false"
     */
    public static final String REDIS_KEY_TENANT_HAS_SPACE_PREFIX = "tenant:has_space:";

    /**
     * 租户到期信息前缀
     * Key格式: tenant:expiration:{tenantId}
     * Value: TenantExpiration对象的JSON字符串
     */
    public static final String REDIS_KEY_TENANT_EXPIRATION_PREFIX = "tenant:expiration:";
}
