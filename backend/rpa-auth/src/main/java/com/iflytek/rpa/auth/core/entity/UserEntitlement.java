package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 用户权益实体类
 *
 * @author system
 */
@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserEntitlement implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    private String id;

    /**
     * 用户ID
     */
    private String userId;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 设计器权限（0-无权限，1-有权限）
     */
    private Integer moduleDesigner;

    /**
     * 执行器权限（0-无权限，1-有权限）
     */
    private Integer moduleExecutor;

    /**
     * 控制台权限（0-无权限，1-有权限）
     */
    private Integer moduleConsole;

    /**
     * 团队市场权限（0-无权限，1-有权限，默认1）
     */
    private Integer moduleMarket;

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
     * 是否删除（0-否，1-是）
     */
    private Integer isDelete;
}
