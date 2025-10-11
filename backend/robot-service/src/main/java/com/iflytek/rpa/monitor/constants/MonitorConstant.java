package com.iflytek.rpa.monitor.constants;

public class MonitorConstant {

    /**
     * excel导出类型，读取XXXXReportGenerator，如RobotReportGenerator
     */
    public static final String REPORT_TYPE_ROBOT = "robot";

    /*=========================统计类型========================================*/
    /**
     * 统计类型-机器人维度
     */
    public static final String AUDIT_OBJECT_TYPE_ROBOT = "robot";

    /**
     * 统计类型-部门维度
     */
    public static final String AUDIT_OBJECT_TYPE_DEPT = "dept";

    /**
     * 统计类型-终端维度
     */
    public static final String AUDIT_OBJECT_TYPE_TERMINAL = "terminal";

    /*=============================数据权限=============================*/

    /**
     * 数据权限-全部
     */
    public static final String DATA_AUTH_TYPE_ALL = "all";

    /**
     * 数据权限-所在部门
     */
    public static final String DATA_AUTH_TYPE_IN_DEPT = "in_dept";

    /**
     * 数据权限-仅自己
     */
    public static final String DATA_AUTH_TYPE_ONLYSELF = "onlyself";

    /**
     * 数据权限-指定部门
     */
    public static final String DATA_AUTH_TYPE_CHECKED_DEPT = "checked_dept";

    /*===========================数据统计进度=======================*/

    /**
     * 待统计
     */
    public static final String AUDIT_STATUS_TO_COUNT = "to_count";

    /**
     * 统计中
     */
    public static final String AUDIT_STATUS_COUNTING = "counting";

    /**
     * 中断
     */
    public static final String AUDIT_STATUS_PENDING = "pending";

    /**
     * 完成
     */
    public static final String AUDIT_STATUS_COMPLETED = "completed";
}
