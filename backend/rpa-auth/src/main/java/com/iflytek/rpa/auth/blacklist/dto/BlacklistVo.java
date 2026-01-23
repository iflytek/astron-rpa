package com.iflytek.rpa.auth.blacklist.dto;

import java.io.Serializable;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 黑名单视图对象
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BlacklistVo implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 记录ID
     */
    private Long id;

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
    private String banReason;

    /**
     * 封禁等级
     */
    private Integer banLevel;

    /**
     * 封禁次数
     */
    private Integer banCount;

    /**
     * 封禁时长（秒）
     */
    private Long banDuration;

    /**
     * 封禁时长描述
     */
    private String banDurationDesc;

    /**
     * 封禁开始时间
     */
    private LocalDateTime startTime;

    /**
     * 封禁结束时间
     */
    private LocalDateTime endTime;

    /**
     * 剩余封禁时间（秒）
     */
    private Long remainingSeconds;

    /**
     * 剩余封禁时间描述
     */
    private String remainingTimeDesc;

    /**
     * 状态（1:生效中, 0:已解封）
     */
    private Integer status;

    /**
     * 状态描述
     */
    private String statusDesc;

    /**
     * 操作人
     */
    private String operator;

    /**
     * 创建时间
     */
    private LocalDateTime createTime;
}
