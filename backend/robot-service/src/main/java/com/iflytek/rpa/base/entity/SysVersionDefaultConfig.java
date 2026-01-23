package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 版本默认配置表实体类
 * 存储每个版本的默认资源配置
 */
@Data
@TableName("sys_version_default_config")
public class SysVersionDefaultConfig implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 版本ID，关联sys_product_version.id
     */
    private Long versionId;

    /**
     * 资源代码（如：designer_count, component_count, executor_count等）
     */
    private String resourceCode;

    /**
     * 资源类型：1-Quota（配额），2-Switch（开关）
     */
    private Integer resourceType;

    /**
     * 父级资源代码（用于层级关系）
     */
    private String parentCode;

    /**
     * 默认值（对于Quota是数量，对于Switch是0或1）
     */
    private Integer defaultValue;

    /**
     * URL路由模式（JSON数组格式，如：["/api/v1/design/**"]）
     */
    private String urlPatterns;

    /**
     * 资源描述
     */
    private String description;

    /**
     * 删除标识：0-未删除，1-已删除
     */
    private Integer deleted;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;
}
