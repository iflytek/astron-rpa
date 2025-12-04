package com.iflytek.rpa.triggerTask.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class TriggerTask implements Serializable {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 触发器计划任务id
     */
    @NotBlank
    private String taskId;

    /**
     * 触发器计划任务名称
     */
    @NotBlank
    private String name;

    /**
     * 构建计划任务的灵活参数
     */
    @NotBlank
    private String taskJson;

    /**
     * 任务类型：定时:schedule、mail、file、hotKey、manual:
     */
    @NotBlank
    private String taskType;

    /**
     * 是否启用 1 启用 ；0 不启用
     */
    private Integer enable;

    /**
     * 报错如何处理：跳过jump、停止stop、重试后跳过retry_jump、重试后停止retry_stop
     */
    @NotBlank
    private String exceptional;

    /**
     * 重试次数
     */
    private Integer retryNum;

    /**
     * 超时时间
     */
    private Integer timeout;

    /**
     * 是否启用排队 1:启用 0:不启用
     */
    private Integer queueEnable;

    private Integer deleted = 0;

    private String creatorId;

    private String tenantId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;
}
