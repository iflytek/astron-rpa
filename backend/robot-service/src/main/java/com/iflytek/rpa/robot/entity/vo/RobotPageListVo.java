package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

@Data
public class RobotPageListVo {
    /**
     * 机器人id（多选框使用）
     */
    String robotId;
    /**
     *
     */
    String robotName;
    /**
     * 创建时间
     */
    String createTime;
    /**
     * 更新时间
     */
    String latestReleaseTime;

    /**
     * 密级标识(密级red/green/yellow)
     */
    String securityLevel;

    /**
     * web类型
     */
    String type;
    /**
     * 所有者id
     */
    String creatorId;
    /**
     * 所有者姓名
     */
    String creatorName;
    /**
     * 所有者手机号
     */
    String creatorPhone;
    /**
     * 所属部门
     */
    String deptName;
    /**
     * 部门路径
     */
    String deptIdPath;

    Integer appVersion;

    Integer version;

    String tenantId;
}
