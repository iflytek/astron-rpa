package com.iflytek.rpa.triggerTask.entity.vo;

import lombok.Data;

import java.util.List;

@Data
public class TriggerTaskVo {
    private String taskId;
    private String name;
    private String taskJson;
    private String taskType;
    private Integer enable;
    private String exceptional;
    private Integer timeout;
    private Integer queueEnable;
    private List<RobotInfoVo> robotInfoVoList;
}
