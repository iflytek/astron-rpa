package com.iflytek.rpa.auth.blacklist.exception;

import lombok.Getter;

/**
 * 应当被拉入黑名单异常
 * 业务代码抛出此异常后，全局异常处理器会自动将用户添加到黑名单
 *
 * @author system
 * @date 2025-12-16
 */
@Getter
public class ShouldBeBlackException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    private final String userId;

    /**
     * 用户名
     */
    private final String username;

    /**
     * 封禁原因
     */
    private final String reason;

    /**
     * 封禁类型
     */
    private final BlackType blackType;

    /**
     * 构造函数
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param reason 封禁原因
     * @param blackType 封禁类型
     */
    public ShouldBeBlackException(String userId, String username, String reason, BlackType blackType) {
        super("用户 " + username + "(" + userId + ") 触发封禁规则: " + reason);
        this.userId = userId;
        this.username = username;
        this.reason = reason;
        this.blackType = blackType;
    }

    /**
     * 构造函数（带原因异常）
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param reason 封禁原因
     * @param blackType 封禁类型
     * @param cause 原因异常
     */
    public ShouldBeBlackException(String userId, String username, String reason, BlackType blackType, Throwable cause) {
        super("用户 " + username + "(" + userId + ") 触发封禁规则: " + reason, cause);
        this.userId = userId;
        this.username = username;
        this.reason = reason;
        this.blackType = blackType;
    }

    /**
     * 封禁类型枚举
     */
    @Getter
    public enum BlackType {
        /**
         * 密码错误次数过多
         */
        PASSWORD_ERROR("密码错误次数过多", 1),

        /**
         * 敏感数据访问
         */
        SENSITIVE_ACCESS("非法访问敏感数据", 2),

        /**
         * 违规操作
         */
        VIOLATION("违规操作", 3),

        /**
         * 手动封禁
         */
        MANUAL("管理员手动封禁", 0);

        private final String description;
        private final int triggerCount;

        BlackType(String description, int triggerCount) {
            this.description = description;
            this.triggerCount = triggerCount;
        }
    }
}
