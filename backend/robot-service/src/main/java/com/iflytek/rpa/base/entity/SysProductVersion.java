package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 产品版本表实体类
 * 存储个人版、专业版、企业版等版本信息
 */
@Data
@TableName("sys_product_version")
public class SysProductVersion implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 版本代码（如：personal, professional, enterprise）
     */
    private String versionCode;

    /**
     * 删除标识：0-未删除，1-已删除
     */
    private Integer deleted;

    /**
     * 创建时间
     */
    private Date createTime;
}
