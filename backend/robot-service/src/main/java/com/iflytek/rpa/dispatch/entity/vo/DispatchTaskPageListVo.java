package com.iflytek.rpa.dispatch.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import lombok.Data;

/**
 * 调度管理计划任务分页查询响应DTO
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Data
public class DispatchTaskPageListVo {

    /**
     * 调度模式计划任务id
     */
    private String dispatchTaskId;
    /**
     * 任务名称
     */
    private String name;
    /**
     * 执行条件：手动触发manual、定时schedule、定时触发trigger
     */
    private String type;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 任务状态：启用中 active、关闭 stop、已过期 expired
     */
    private String status;

    /**
     * 构建调度计划任务的灵活参数;定时schedule存计划执行的对应JSON
     */
    private String cronJson;

    /**
     * 执行终端/分组
     */
    private List<TerminalOrGroup> terminalOrGroupList = new ArrayList<>();

    private List<DispatchRobot> dispatchRobotList = new ArrayList<>();

    @Data
    public static class TerminalOrGroup {
        /**
         * 分组-id; 终端-terminalId
         */
        private String id;
        /**
         * 终端名/分组名
         */
        private String name;
        /**
         * 终端：terminal、分组：group
         */
        private String type;
        /**
         * 次序
         */
        private Integer sort;
        /**
         * 终端状态
         */
        private String status;
        /**
         * 终端数量
         */
        private Integer num;
    }

    @Data
    public static class DispatchRobot {
        private String name;
        /**
         * 机器人id
         */
        private String robotId;
        /**
         * 是否启用版本
         */
        private Boolean online;
        /**
         * 机器人版本
         */
        private Integer version;
        /**
         * 次序
         */
        private Integer sort;
        /**
         * 是否有配置参数
         */
        private Boolean haveParam;
        /**
         * 配置参数
         */
        private String paramJson;
    }

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
}
