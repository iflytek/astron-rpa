package com.iflytek.rpa.market.entity.bo;

import com.iflytek.rpa.robot.entity.RobotExecute;
import lombok.Data;

@Data
public class PublishInfoBo {
    RobotExecute robotExecute;
    Integer nextVersion;
}
