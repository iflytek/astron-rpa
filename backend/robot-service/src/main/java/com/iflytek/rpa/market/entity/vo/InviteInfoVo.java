package com.iflytek.rpa.market.entity.vo;

import lombok.Data;

/**
 * 邀请信息响应VO
 */
@Data
public class InviteInfoVo extends AcceptResultVo {
    /**
     * 邀请人姓名
     */
    private String inviterName;

    /**
     * 团队名称
     */
    private String marketName;
}
