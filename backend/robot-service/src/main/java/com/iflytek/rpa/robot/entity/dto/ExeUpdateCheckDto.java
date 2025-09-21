package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class ExeUpdateCheckDto {
    // 逗号隔开，互相对应
    String robotIdListStr;
    String appIdListStr;
}
