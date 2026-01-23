package com.iflytek.rpa.auth.core.entity;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 租户对象
 *
 * @author wanchen2
 */
@JsonIgnoreProperties(ignoreUnknown = true)
@Data
public class Tenant implements Serializable {

    private static final long serialVersionUID = 2231322704057975086L;

    /**
     * 主键ID
     */
    private String id;

    /**
     * 租户名称
     */
    private String name;

    /**
     * 租户编码
     */
    private String tenantCode;

    /**
     * 租户状态 {0停用 1启用}
     */
    private Integer status;

    /**
     * 备注
     */
    private String remark;

    /**
     * 创建人
     */
    private String creator;

    /**
     * 是否删除
     */
    private Integer isDelete;

    /**
     * 是否默认租户
     */
    private Boolean isDefaultTenant;

    /**
     * 租户类型
     */
    private String tenantType;

    /*
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
     * 到期时间（格式：YYYY-MM-DD）
     * 个人版和买断企业版返回null（不限期）
     */
    private String expirationDate;

    /**
     * 剩余天数
     * 个人版和买断企业版返回null（不限期）
     * 已到期返回负数
     */
    private Long remainingDays;

    /**
     * 是否到期
     * 个人版和买断企业版返回false（不限期）
     */
    private Boolean isExpired;

    /**
     * 是否提示到期（到期前N天需要提醒）
     * 个人版和买断企业版返回false（不限期）
     */
    private Boolean shouldAlert;
}
