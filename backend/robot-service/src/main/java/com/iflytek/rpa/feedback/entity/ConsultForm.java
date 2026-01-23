package com.iflytek.rpa.feedback.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 咨询表单实体类
 *
 * @author system
 * @since 2024-12-15
 */
@Data
@TableName("consult_form")
public class ConsultForm implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 表单类型 1=专业版 2=企业版 预留 3~99
     */
    private Integer formType;

    /**
     * 公司名称
     */
    private String companyName;

    /**
     * 联系人姓名
     */
    private String contactName;

    /**
     * 手机号
     */
    private String mobile;

    /**
     * 邮箱（非必填）
     */
    private String email;

    /**
     * 团队人数区间（字典值）
     */
    private String teamSize;

    /**
     * 状态 0=待处理 1=已处理 2=已忽略
     */
    private Integer status;

    /**
     * 客服备注
     */
    private String remark;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createdAt;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updatedAt;
}
