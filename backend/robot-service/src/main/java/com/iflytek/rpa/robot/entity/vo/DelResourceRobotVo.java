package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

import java.util.List;

@Data
public class DelResourceRobotVo {
    /**
     * 机器人引用关系表
     */
    List<TaskReferInfo> taskReferInfoList;

    /**
     * 机器人Id
     */
    String robotId;
}