package com.iflytek.rpa.feedback.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 反馈举报表实体类
 *
 * @author system
 * @since 2024-12-15
 */
@Data
@TableName("feedback_report")
public class FeedbackReport implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 唯一编号
     */
    private String reportNo;

    /**
     * 用户登录名
     */
    private String username;

    /**
     * 问题分类列表（JSON格式）
     * 格式：{"内容安全类":["生成违法/违规信息","核心内容"],"功能缺陷类":["生成流程代码错误，无法执行"]}
     */
    private String categories;

    /**
     * 问题描述
     */
    private String description;

    /**
     * 图片文件ID列表（逗号分隔）
     */
    private String imageIds;

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
     * 逻辑删除标志 0:未删除 1:已删除
     */
    private Integer deleted;

    /**
     * 是否已处理 0:未处理 1:已处理
     */
    private Integer processed;
}
