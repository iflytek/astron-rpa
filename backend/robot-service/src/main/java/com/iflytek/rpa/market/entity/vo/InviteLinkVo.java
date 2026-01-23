package com.iflytek.rpa.market.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * 邀请链接响应VO
 */
@Data
public class InviteLinkVo {
    /**
     * 邀请密钥
     */
    private String inviteKey;

    /**
     * 过期期限
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date expireTime;

    /**
     * 失效时间类型：4小时、24小时、7天、30天
     * 对应值：4H, 24H, 7D, 30D
     */
    private String expireType;
    /**
     * 是否超过人数限制：0-未超过，1-超过
     */
    private Integer overNumLimit;
}
