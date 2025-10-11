package com.iflytek.rpa.market.entity.dto;

import com.iflytek.rpa.robot.entity.RobotVersion;
import lombok.Data;

@Data
public class ResVerDto extends RobotVersion {
    String appId;
    Integer latestAppVersion;
    String marketId;
    String robotId;
    String introduction;
    String useDescription;
    String iconUrl;
}
