package com.iflytek.rpa.dispatch.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class DispatchTaskRobotExecuteRecordVo {

    /**
     * id
     */
    private String id;

    /**
     * 机器人执行id
     */
    private String executeId;

    /**
     * 调度模式计划任务执行id
     */
    private String dispatchTaskExecuteId;

    /**
     * 机器人id
     */
    private String robotId;

    /**
     * 机器人名称
     */
    private String robotName;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startTime;

    /**
     * 结束时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date endTime;

    /**
     * 执行耗时 单位秒
     */
    private Long executeTime;

    /**
     * 执行结果枚举：robotFail:失败， robotSuccess:成功，robotCancel:取消(中止)，robotExecute:正在执行
     */
    private String result;

    /**
     * 机器人配置参数
     */
    private String paramJson;

    /**
     * 错误原因
     */
    private String errorReason;

    /**
     * 日志内容
     */
    private String executeLog;

    /**
     * 视频记录的本地存储路径
     */
    private String videoLocalPath;

    /**
     * 部门全路径编码
     */
    private String deptIdPath;

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
}
