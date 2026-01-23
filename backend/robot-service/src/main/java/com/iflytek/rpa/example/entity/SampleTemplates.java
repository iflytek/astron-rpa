package com.iflytek.rpa.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 系统预定义的模板库(SampleTemplates)实体类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class SampleTemplates implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 样例id
     */
    private String sampleId;

    /**
     * 模版名称
     */
    private String name;

    /**
     * 模板类型：robot_design, robot_execute, schedule_task 等
     */
    private String type;

    /**
     * 模板语义化版本号（如 1.2.0）
     */
    private String version;

    /**
     * 模板配置数据（JSON 格式），数据库一行的数据
     */
    private String data;

    /**
     * 模板说明
     */
    private String description;

    /**
     * 是否启用（false 则新用户不注入）
     */
    private Integer isActive;

    /**
     * 逻辑删除标记（避免物理删除）
     */
    private Integer isDeleted;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createdTime;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updatedTime;
}
