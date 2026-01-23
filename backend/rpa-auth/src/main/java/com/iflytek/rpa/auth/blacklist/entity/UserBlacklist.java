package com.iflytek.rpa.auth.blacklist.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.io.Serializable;
import java.time.LocalDateTime;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 用户黑名单实体类
 *
 * @author system
 * @date 2025-12-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("user_blacklist")
public class UserBlacklist implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 用户ID
     */
    @TableField("user_id")
    private String userId;

    /**
     * 用户名
     */
    @TableField("username")
    private String username;

    /**
     * 封禁原因
     */
    @TableField("ban_reason")
    private String banReason;

    /**
     * 封禁等级(1,2,3...)
     */
    @TableField("ban_level")
    private Integer banLevel;

    /**
     * 封禁次数
     */
    @TableField("ban_count")
    private Integer banCount;

    /**
     * 封禁时长(秒)
     */
    @TableField("ban_duration")
    private Long banDuration;

    /**
     * 封禁开始时间
     */
    @TableField("start_time")
    private LocalDateTime startTime;

    /**
     * 封禁结束时间
     */
    @TableField("end_time")
    private LocalDateTime endTime;

    /**
     * 状态(1:生效中, 0:已解封)
     */
    @TableField("status")
    private Integer status;

    /**
     * 操作人
     */
    @TableField("operator")
    private String operator;

    /**
     * 创建时间
     */
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    /**
     * 更新时间
     */
    @TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
}
