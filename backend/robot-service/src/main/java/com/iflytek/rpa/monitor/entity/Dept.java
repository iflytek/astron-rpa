package com.iflytek.rpa.monitor.entity;

import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 部门表(Dept)实体类
 *
 * @author mjren
 * @since 2023-04-12 16:51:49
 */
@Data
public class Dept implements Serializable {
    private static final long serialVersionUID = 291098741550425142L;
    /**
     * 主键
     */
    private Long id;
    /**
     * 部门名称
     */
    private String name;
    /**
     * 部门全名
     */
    private String allName;
    /**
     * 上级部门id
     */
    private Long parentId;

    private Integer sort;
    /**
     * 删除标志
     */
    private Integer deleted;

    private String tenantId;

    private Date createTime;

    private Date updateTime;

    private String creatorId;

    private Long updateBy;

    private String deptIdPath;
}
