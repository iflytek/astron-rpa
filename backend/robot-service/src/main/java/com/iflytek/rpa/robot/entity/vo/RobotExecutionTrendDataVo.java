package com.iflytek.rpa.robot.entity.vo;


import lombok.Data;

import java.util.List;

@Data
public class RobotExecutionTrendDataVo {
    /**
     * 日列表
     */
    List<RobotExecutionTrendData> dayList;
    /**
     * 月列表
     */
    List<RobotExecutionTrendData> monthList;
}