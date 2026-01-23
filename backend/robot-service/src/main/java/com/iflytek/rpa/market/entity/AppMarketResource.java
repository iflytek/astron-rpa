package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * 团队市场-资源映射表(AppMarketResource)实体类
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
@Data
public class AppMarketResource implements Serializable {
    private static final long serialVersionUID = 596242538092112354L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 团队市场id
     */
//    @NotBlank(message = "市场id不能为空")
    private String marketId;
    /**
     * 应用id，模板id，组件id
     */
    private String appId;
    /**
     * 下载次数
     */
    private Long downloadNum;
    /**
     * 查看次数
     */
    private Long checkNum;
    /**
     * 发布人
     */
    private String creatorId;
    /**
     * 发布时间
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

    private String tenantId;
    /**
     * 机器人id
     */
    private String robotId;
    /**
     * 资源名称
     */
    private String appName;


    /**
     * 密级标识: red,yellow,green
     */
    @TableField(exist = false)
    private String security_level;

    /**
     * 使用期限截止时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    @TableField(exist = false)
    private Date expiry_date;

    @TableField(exist = false)
    private String expiry_date_str;
}

