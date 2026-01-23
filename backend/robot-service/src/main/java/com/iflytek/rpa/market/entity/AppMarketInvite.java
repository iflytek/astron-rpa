package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 团队市场-邀请链接表(AppMarketInvite)实体类
 */
@Data
public class AppMarketInvite implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 邀请链接key
     */
    private String inviteKey;

    /**
     * 市场id
     */
    private String marketId;

    /**
     * 邀请人id
     */
    private String inviterId;

    /**
     * 失效时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date expireTime;
    /**
     * 失效时间类型：4小时、24小时、7天、30天
     * 对应值：4H, 24H, 7D, 30D
     */
    private String expireType;
    /**
     * 当前已加入人数
     */
    private Integer currentJoinCount;
    /**
     * 最大加入人数
     */
    private Integer maxJoinCount;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新者id
     */
    private String updaterId;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    @TableLogic(value = "0", delval = "1")
    private Integer deleted;
}
