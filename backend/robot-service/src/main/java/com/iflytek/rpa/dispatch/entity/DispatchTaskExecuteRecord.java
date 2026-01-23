package com.iflytek.rpa.dispatch.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 调度模式-计划任务执行记录实体类
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Data
@TableName("dispatch_task_execute_record")
public class DispatchTaskExecuteRecord implements Serializable {
    private static final long serialVersionUID = 221173423657136377L;

    /**
     * 主键id
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 调度模式计划任务id
     */
    private Long dispatchTaskId;

    /**
     * 调度模式计划任务执行id
     */
    private Long dispatchTaskExecuteId;

    /**
     * 执行批次，1，2，3....
     */
    private Integer count;

    /**
     * 触发条件：手动触发manual、定时schedule、定时触发trigger
     */
    private String dispatchTaskType;

    /**
     * 执行结果枚举:成功success、失败error、执行中executing、中止cancel、下发失败dispatch_error
     */
    private String result;

    /**
     * 任务详情json数据，用于重试时回查参数
     */
    private String taskDetailJson;

    /**
     * 执行开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startTime;

    /**
     * 执行结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date endTime;

    /**
     * 执行耗时 单位秒
     */
    private Long executeTime;

    /**
     * 终端唯一标识，如设备mac地址
     */
    private String terminalId;

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
