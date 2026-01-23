package com.iflytek.rpa.dispatch.entity;

import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 调度模式-计划任务实体类
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Data
@TableName("dispatch_task")
public class DispatchTask implements Serializable {
    private static final long serialVersionUID = 221173423657236377L;

    /**
     * 调度模式计划任务id
     */
    @TableId
    private String dispatchTaskId;

    /**
     * 任务状态：启用中 active、关闭 stop、已过期 expired
     */
    private String status;

    /**
     * 调度模式计划任务名称
     */
    private String name;

    /**
     * 构建调度计划任务的灵活参数;定时schedule存计划执行的对应JSON
     */
    private String cronJson;

    /**
     * 触发条件：手动触发manual、定时schedule、定时触发trigger
     */
    private String type;

    /**
     * 报错如何处理：跳过jump、停止stop、重试后跳过retry_jump、重试后停止retry_stop
     */
    private String exceptional;

    /**
     * 重试次数
     */
    private Integer retryNum;

    /**
     * 是否启用超时时间 1:启用 0:不启用
     */
    private Boolean timeoutEnable;

    /**
     * 超时时间
     */
    private Integer timeout;

    /**
     * 是否启用排队 1:启用 0:不启用
     */
    private Boolean queueEnable;

    /**
     * 是否开启录屏 1:启用 0:不启用
     */
    private Boolean screenRecordEnable;

    /**
     * 是否开启虚拟桌面 1:启用 0:不启用
     */
    private Boolean virtualDesktopEnable;

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
