package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

@Data
public class ProcessModuleListDto {
    String robotId; // 机器人idprocessModuleList
    private String mode = EDIT_PAGE;
    Integer robotVersion; // 机器人版本
}
