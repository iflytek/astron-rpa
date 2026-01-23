package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;

/**
 * (AppMarketDict)实体类
 *
 * @author mjren
 * @since 2024-03-25 10:44:06
 */
@Data
public class AppMarketDict implements Serializable {
    private static final long serialVersionUID = -18658781229065808L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
/**
     * 业务编码：1、行业类型，2、角色功能marketRoleFunc
     */
    private String businessCode;
/**
     * 行业名称，角色功能名称
     */
    private String name;
/**
     * 行业编码，功能编码
     */
    private String dictCode;
/**
     * T有权限，F无权限
     */
    private String dictValue;
/**
     * 市场所有者，管理员，普通用户
     */
    private String userType;
/**
     * 描述
     */
    private String description;
/**
     * 排序
     */
    private Integer seq;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;

    private Integer deleted;

}

