package com.iflytek.rpa.market.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * (TenantUser)实体类
 *
 * @author mjren
 * @since 2023-04-19 09:53:20
 */
@Data
public class TenantUser implements Serializable {
    private static final long serialVersionUID = 334855698665464892L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String tenantId;

    private String userId;

    private String phone;
    /**
     * 用户名
     */
    private String name;
    /**
     * 姓名
     */
    private String realName;

    private String jobNo;
    /**
     * 邮箱
     */
    private String mail;
    /**
     * 性别 0女 1男
     */
    private Integer gender;
    /**
     * 0待激活 1禁用 2启用
     */
    private Integer activeStatus;
    /**
     * 0启用 1禁用
     */
    private Integer status;

    private Integer deleted;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    private String creatorId;

    private Long updateBy;

    private String deptIdPath;
}
