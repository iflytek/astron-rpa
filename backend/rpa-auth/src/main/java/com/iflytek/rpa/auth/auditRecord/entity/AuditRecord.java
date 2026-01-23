package com.iflytek.rpa.auth.auditRecord.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import java.util.List;
import lombok.Data;

/**
 * 审计日志表
 * @author jqfang3
 * @since 2025-08-04
 */
@Data
@TableName("audit_record")
public class AuditRecord implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 事件模块代码
     */
    private Integer eventModuleCode;

    /**
     * 事件模块
     */
    private String eventModuleName;

    /**
     * 事件代码
     */
    private Integer eventTypeCode;

    /**
     * 事件类型
     */
    private String eventTypeName;

    /**
     * 事件详情
     */
    private String eventDetail;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 创建者名称
     */
    private String creatorName;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 角色名称列表（非数据库字段）
     */
    @TableField(exist = false)
    private List<String> roleNames;

    /**
     * 用户ID（非数据库字段）
     */
    @TableField(exist = false)
    private String userId;
}
