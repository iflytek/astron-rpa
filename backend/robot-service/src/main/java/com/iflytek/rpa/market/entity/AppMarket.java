package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 团队市场-团队表(AppMarket)实体类
 *
 * @author makejava
 * @since 2024-01-19 14:41:33
 */
@Data
public class AppMarket implements Serializable {
    private static final long serialVersionUID = -41282788033507896L;
    /**
     * 团队市场id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String marketId;
    /**
     * 市场名称
     */
    private String marketName;
    /**
     * 市场分享
     */
    private String marketShare;
    /**
     * 应用分享
     */
    private String appShare;
    /**
     * 市场描述
     */
    private String marketDescribe;
    /**
     * 市场类型：team,official
     */
    private String marketType;
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

    private Boolean toDissolve;

    private String userType;

    private String userName;

    private String tenantId;

    private String newOwner;
}
