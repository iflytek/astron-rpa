package com.iflytek.rpa.market.entity.dto;

import lombok.Data;

/**
 * 生成邀请链接请求DTO
 */
@Data
public class InviteLinkDto {
    /**
     * 市场id
     */
    private String marketId;

    /**
     * 失效时间类型：4小时、24小时、7天、30天
     * 对应值：4H, 24H, 7D, 30D
     */
    private String expireType;
}
