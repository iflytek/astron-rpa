package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

@Data
public class LatestVersionRobotVo {
    /**
     * 机器人id
     */
    String robotId;
    /**
     * 最新版本号
     */
    Integer latestVersion;
    /**
     * 上架申请状态 pending:申请中 approved:申请已通过 none:无申请记录 null:上架审核未开启
     */
    String applicationStatus;
}
