package com.iflytek.rpa.dispatch.entity.dto;

import com.iflytek.rpa.dispatch.entity.DispatchTaskRobotExecuteRecord;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class RobotExecuteStatusDto extends DispatchTaskRobotExecuteRecord {
    /*
     * 机器人执行id
     */
    //    @NotNull(message = "机器人执行ID不能为空")
    private Long executeId;

    /*
     * 机器人id
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /*
     * 机器人版本
     */
    @NotNull(message = "机器人版本不能为空")
    private Integer robotVersion;

    /*
     * 任务执行ID
     */
    @NotNull(message = "任务执行ID不能为空")
    private Long dispatchTaskExecuteId;

    /*
     * 终端ID
     */
    private String terminalId;

    /*
     * 任务执行状态, 枚举  执行结果枚举:：robotFail:失败， robotSuccess:成功，robotCancel:取消(中止)，robotExecute:正在执行
     */
    private String result;

    /*
     * 错误原因
     */
    private String error_reason;

    /**
     * 机器人配置参数
     */
    private String paramJson;

    /*
     * 执行日志
     */
    private String executeLog;

    /*
     * 视频本地保存路径
     */
    private String videoLocalPath;

    private String dataTablePath;
}
