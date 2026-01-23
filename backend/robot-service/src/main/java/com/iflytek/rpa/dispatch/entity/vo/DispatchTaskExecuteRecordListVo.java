package com.iflytek.rpa.dispatch.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class DispatchTaskExecuteRecordListVo {

    /**
     * 任务执行ID
     */
    private String dispatchTaskExecuteId;

    /**
     * 任务ID
     */
    private String dispatchTaskId;

    /**
     * 终端信息
     */
    private TerminalInfo terminalInfo;

    /**
     * 任务名称
     */
    private String taskName;

    /**
     * 任务执行批次
     */
    private Integer count;

    /**
     * 任务类型 手动：manual、定时：schedule、邮件：mail、文件：file、热键：hotKey
     */
    private String dispatchTaskType;

    /**
     * 任务开始时间
     */
    private String taskStartTime;

    /**
     * 任务结束时间
     */
    private String taskEndTime;

    /**
     * 任务执行耗时
     */
    private Long taskExecuteTime;

    /**
     * 任务状态：
     * 成功：success、启动失败：start_error、执行失败：exe_error、取消：cancel、执行中：executing
     */
    private String taskExecuteStatus;

    /**
     * 机器人执行记录列表
     */
    private List<DispatchTaskRobotExecuteRecordVo> robotExecuteRecordList;

    /**
     * 终端信息内部类
     */
    @Data
    public static class TerminalInfo {
        /**
         * 终端ID
         */
        private String terminalId;

        /**
         * 用户名
         */
        private String userName;

        /**
         * 终端操作系统
         */
        private String os;

        /**
         * 终端设备用户名
         */
        private String osName;

        /**
         * 终端操作系统密码
         */
        private String osPwd;

        /**
         * 终端名称
         */
        private String terminalName;

        /**
         * 终端端口
         */
        private Integer port;

        /**
         * 终端自定义端口
         */
        private Integer customPort;

        /**
         * 终端IP
         */
        private String ip;

        /**
         * 终端自定义IP
         */
        private String customIp;

        /**
         * 终端实际客户端IP
         */
        private String actualClientIp;
    }
}
