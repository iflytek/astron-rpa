package com.iflytek.rpa.auth.sp.uap.entity;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 租户到期信息实体类
 *
 * @author system
 */
@Data
public class TenantExpiration implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    private String id;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 到期时间（格式：YYYY-MM-DD）
     * 对于非买断企业版，此字段存储的是加密后的数据
     * 对于专业版，此字段存储的是明文数据
     */
    private String expirationDate;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除（0-否，1-是）
     */
    private Integer isDelete;
}
