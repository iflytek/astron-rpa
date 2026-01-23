package com.iflytek.rpa.dispatch.entity.vo;

import java.util.ArrayList;
import java.util.List;
import lombok.Builder;
import lombok.Data;

/**
 * 终端任务详情VO
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Data
@Builder
public class TerminalTaskDetailVo {

    /**
     * 终端ID
     */
    private String terminalId;

    /**
     * 任务信息列表
     */
    @Builder.Default
    private List<DispatchTaskInfo> dispatchTaskInfos = new ArrayList<>();

    @Builder.Default
    private List<DispatchTaskInfo> retryTaskInfos = new ArrayList<>();

    @Builder.Default
    private List<DispatchTaskInfo> stopTaskInfos = new ArrayList<>();

    @Data
    public static class DispatchTaskInfo {
        /**
         * 任务ID
         */
        private String taskId;

        /**
         * 任务名称
         */
        private String taskName;

        /**
         * 任务类型（手动/计划/定时）
         */
        private String taskType;

        /**
         * 任务执行的调度信息
         */
        private String cronJson;

        /**
         * 任务状态
         */
        private String taskStatus;

        /**
         * 报错处理策略
         */
        private String exceptional;

        /**
         * 超时时间
         */
        private Integer timeout;
        /**
         * 超时时间是否开启
         */
        private Integer timeoutEnable;

        /**
         * 重试次数
         */
        private Integer retryNum;
        /**
         * 队列是否开启
         */
        private Integer queueEnable;

        /**
         * 屏幕录制是否开启
         */
        private Integer screenRecordEnable;

        /**
         * 虚拟桌面是否开启
         */
        private Integer virtualDesktopEnable;

        /**
         * 机器人信息列表
         */
        private List<DispatchRobotInfo> dispatchRobotInfos = new ArrayList<>();
    }

    @Data
    public static class DispatchRobotInfo {
        /**
         * 任务ID
         */
        private String taskId;

        /**
         * 机器人ID
         */
        private String robotId;

        /**
         * 机器人名称
         */
        private String robotName;

        /**
         * 机器人版本
         */
        private String robotVersion;

        /**
         * 是否在线版本
         */
        private Integer online;

        /**
         * 参数JSON字符串
         */
        private String paramJson;

        /**
         * 排序
         */
        private Integer sort;

        //        /**
        //         * 流程信息列表
        //         */
        //        private List<DispatchProcessInfo> dispatchProcessInfos;
        //
        //        /**
        //         * 代码模块列表
        //         */
        //        private List<DispatchModuleInfo> modules;
        //
        //        /**
        //         * 全局参数列表
        //         */
        //        private List<DispatchGlobalParam> dispatchGlobalParams;
        //
        //        /**
        //         * 依赖包列表
        //         */
        //        private List<DispatchRequirement> dispatchRequirements;
    }

    @Data
    public static class DispatchProcessInfo {
        /**
         * 流程ID
         */
        private String processId;

        /**
         * 流程信息
         */
        private String processContent;

        /**
         * 流程名称
         */
        private String processName;

        /**
         * 参数列表
         */
        private List<DispatchParam> dispatchParams = new ArrayList<>();
    }

    @Data
    public static class DispatchModuleInfo {
        /**
         * 代码模块ID
         */
        private String moduleId;

        /**
         * 模块内容
         */
        private String moduleContent;

        /**
         * 模块名称
         */
        private String moduleName;
    }

    @Data
    public static class DispatchGlobalParam {
        /**
         * 参数名称
         */
        private String varName;

        /**
         * 参数类型
         */
        private String varType;

        /**
         * 参数值
         */
        private String varValue;

        /**
         * 参数描述
         */
        private String varDescribe;
    }

    @Data
    public static class DispatchRequirement {
        /**
         * 包名
         */
        private String packageName;

        /**
         * 版本
         */
        private String packageVersion;

        /**
         * 镜像地址
         */
        private String mirror;
    }

    @Data
    public static class DispatchParam {
        /**
         * 参数ID
         */
        private String id;

        /**
         * 输入/输出
         */
        private String varDirection;

        /**
         * 参数名称
         */
        private String varName;

        /**
         * 参数类型
         */
        private String varType;

        /**
         * 参数值
         */
        private String varValue;

        /**
         * 参数描述
         */
        private String varDescribe;

        /**
         * 流程ID
         */
        private String processId;
    }
}
