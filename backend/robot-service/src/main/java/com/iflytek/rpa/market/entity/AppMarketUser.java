package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 团队市场-人员表，n:n的关系(AppMarketUser)实体类
 *
 * @author makejava
 * @since 2024-01-19 14:41:35
 */
@Data
public class AppMarketUser implements Serializable {
    private static final long serialVersionUID = -77353675644566502L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 根据id找在对应租户的信息
     */
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
     * 被邀请人
     */
    private String creatorId;
    /**
     * 加入时间
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
