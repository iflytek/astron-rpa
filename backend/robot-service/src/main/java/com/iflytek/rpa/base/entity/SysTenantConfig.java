package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 租户配置表实体类
 * 存储每个租户的资源配额配置快照
 */
@Data
@TableName("sys_tenant_config")
public class SysTenantConfig implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 版本ID，关联sys_product_version.id
     */
    private Long versionId;

    /**
     * 全量配置快照（JSON格式）
     * 格式：
     * {
     *   "resource_code": {
     *     "type": "QUOTA/SWITCH",
     *     "base": 19,
     *     "final": 100
     *   }
     * }
     */
    private String extraConfigJson;

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
