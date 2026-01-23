package com.iflytek.rpa.dispatch.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 调度模式-计划任务与机器人映射表实体类
 *
 * @author jqfang3
 * @since 2025-08-15
 */
@Data
@TableName("dispatch_task_robot")
public class DispatchTaskRobot implements Serializable {
    private static final long serialVersionUID = 221173423657236317L;

    /**
     * 主键id
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 调度模式计划任务id
     */
    private String dispatchTaskId;

    /**
     * 机器人ID
     */
    private String robotId;

    /**
     * 机器人版本
     */
    private Integer version;
    /**
     * 是否启用版本： 0:未启用,1:已启用
     */
    private Boolean online;
    /**
     * 机器人配置参数
     */
    private String paramJson;

    /**
     * 排序, 越小越靠前
     */
    private Integer sort;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 更新者id
     */
    private String updaterId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}
