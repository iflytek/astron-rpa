package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

import java.util.List;

@Data
public class MarketRobotDetailVo {

    MyRobotDetailVo myRobotDetailVo;

    // 原版本信息
    String sourceName;
    List<VersionInfo> versionInfoList;

}
