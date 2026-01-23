package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

@Data
public class RobotIconVo {
    private String iconUrl;
    private String name;

    public RobotIconVo(String name, String iconUrl) {
        this.name = name;
        this.iconUrl = iconUrl;
    }
}
