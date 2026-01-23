package com.iflytek.rpa.auth.blacklist.dto;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 黑名单缓存 DTO
 * 用于 Redis 缓存
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BlacklistCacheDto implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 用户名
     */
    private String username;

    /**
     * 封禁原因
     */
    private String reason;

    /**
     * 封禁等级
     */
    private Integer level;

    /**
     * 封禁次数
     */
    private Integer count;

    /**
     * 封禁结束时间（时间戳，毫秒）
     */
    private Long endTimeMillis;

    /**
     * 剩余封禁时间（秒）
     */
    private Long remainingSeconds;
}
