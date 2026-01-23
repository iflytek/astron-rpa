package com.iflytek.rpa.dispatch.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 调度模式-计划任务-终端映射表实体类
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Data
@TableName("dispatch_task_terminal")
public class DispatchTaskTerminal implements Serializable {
    private static final long serialVersionUID = 113373423657236317L;

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
     * 触发条件：终端terminal、终端分组group
     */
    private String terminalOrGroup;

    /**
     * 执行方式：随机一台random_one、全部执行all
     */
    private String executeMethod;

    /**
     * 具体值：存储 list<id>
     */
    private String value;
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
