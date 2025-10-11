package com.iflytek.rpa.market.entity.vo;

import com.iflytek.rpa.robot.entity.vo.VersionInfo;
import lombok.Data;

@Data
public class AppDetailVersionInfo extends VersionInfo {
    String updateLog;
}
