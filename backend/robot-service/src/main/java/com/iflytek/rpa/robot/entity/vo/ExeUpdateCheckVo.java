package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

@Data
public class ExeUpdateCheckVo {
    String robotId;
    String appId;
    Integer updateStatus; // 0: 不提示更新 1: 提示更新
}
