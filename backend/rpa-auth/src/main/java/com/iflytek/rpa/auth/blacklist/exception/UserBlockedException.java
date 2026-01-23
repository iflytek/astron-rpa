package com.iflytek.rpa.auth.blacklist.exception;

import java.time.LocalDateTime;
import lombok.Getter;

/**
 * 用户被封禁异常
 *
 * @author system
 * @date 2025-12-16
 */
@Getter
public class UserBlockedException extends RuntimeException {

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
     * 封禁结束时间
     */
    private final LocalDateTime endTime;

    /**
     * 剩余封禁时间（秒）
     */
    private final Long remainingSeconds;

    /**
     * 构造函数
     *
     * @param userId 用户ID
     * @param username 用户名
     * @param reason 封禁原因
     * @param endTime 封禁结束时间
     * @param remainingSeconds 剩余封禁时间（秒）
     */
    public UserBlockedException(
            String userId, String username, String reason, LocalDateTime endTime, Long remainingSeconds) {
        super(buildMessage(username, reason, endTime, remainingSeconds));
        this.userId = userId;
        this.username = username;
        this.reason = reason;
        this.endTime = endTime;
        this.remainingSeconds = remainingSeconds;
    }

    /**
     * 构建异常消息
     */
    private static String buildMessage(String username, String reason, LocalDateTime endTime, Long remainingSeconds) {
        long days = remainingSeconds / 86400;
        long hours = (remainingSeconds % 86400) / 3600;
        long minutes = (remainingSeconds % 3600) / 60;

        StringBuilder sb = new StringBuilder();
        sb.append("账号 ").append(username).append(" 已被封禁");
        if (reason != null && !reason.isEmpty()) {
            sb.append("，原因：").append(reason);
        }
        sb.append("。剩余封禁时间：");
        if (days > 0) {
            sb.append(days).append("天");
        }
        if (hours > 0) {
            sb.append(hours).append("小时");
        }
        if (minutes > 0) {
            sb.append(minutes).append("分钟");
        }
        if (days == 0 && hours == 0 && minutes == 0) {
            sb.append(remainingSeconds).append("秒");
        }
        return sb.toString();
    }
}
