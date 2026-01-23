package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2024-01-22 11:04
 * @copyright Copyright (c) 2024 mjren
 */
@Data
public class MarketDto {
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String tenantId;
    /**
     * 市场id
     */
    private String marketId;
    /**
     * 成员类型：admin,consumer
     */
    private String userType;
    /**
     *
     */
    private String creatorId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 应用名称
     */
    private String appName;

    private String appId;

    private Integer appVersion;

    /**
     * 政务，烟草
     */
    private String dictName;

    /**
     * 简介
     */
    private String appIntro;

    /**
     * 使用说明
     */
    private String useIntro;

    private Boolean isCreator;

    /**
     * 所有者
     */
    private String ownerName;

    private Long ownerId;

    /**
     * 市场名称
     */
    private String marketName;

    private Boolean isAdded;

    private String userName;

    private String realName;

    private String email;

    private String phone;

    private Integer deleted;

    private Boolean isAdmin;

    private Boolean haveSharePrivate;

    private List<AppMarketVersion> appMarketVersionList;

    private Integer pageNo;

    private Integer pageSize;

    private List<String> marketIdList;

    /**
     * 如update_time
     */
    private String sortBy;

    /**
     * desc或asc
     */
    private String sortType;

    private List<AppMarketUser> userInfoList;

    private String resourceStatus;

    private String robotId;

    private String componentId;

    private Integer updateVersionNum;

    private List<String> userIdList;

    public MarketDto() {}

    public MarketDto(String tenantId, String marketId, String appId) {
        this.marketId = marketId;
        this.tenantId = tenantId;
        this.appId = appId;
    }
}
