package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

@Data
public class ShareDesignDto {
    // 机器人id
    String robotId;
    // 分享机器人的用户id
    String sharedUserId;
    // 分享机器人用户的租户id
    String sharedTenantId;
    // 接收机器人的用户id
    String receivedUserId;
    // 接收机器人用户的租户id
    String receivedTenantId;
}
