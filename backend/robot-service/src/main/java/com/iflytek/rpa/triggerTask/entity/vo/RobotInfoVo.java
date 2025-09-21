package com.iflytek.rpa.triggerTask.entity.vo;

import com.iflytek.rpa.task.entity.dto.RobotInfo;
import lombok.Data;

@Data
public class RobotInfoVo extends RobotInfo {

    Integer sort; // 序列
    String robotName; // 机器人名称
    /**
     * task_robot表的id，用来区分一个计划任务内多个相同的机器人
     */
    private Long id;
    /**
     * 是否有配置参数
     */
    private Boolean haveParam;
}
