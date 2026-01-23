package com.iflytek.rpa.dispatch.entity.dto;

import com.iflytek.rpa.dispatch.entity.DispatchTaskExecuteRecord;
import lombok.Data;

@Data
public class TaskExecuteStatusDto extends DispatchTaskExecuteRecord {
    /*
     * 任务ID
     */
    private Long dispatchTaskId;

    /*
     * 任务执行ID
     */
    private Long dispatchTaskExecuteId;

    /*
     * 终端ID
     */
    private String terminalId;

    /*
     * 任务执行状态, 枚举  成功  "success"     # 启动失败     "start_error"     # 执行失败      "exe_error"     # 取消     CANCEL = "cancel"     # 执行中   "executing"
     */
    private String result;
}
