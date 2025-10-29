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
 * 用户从系统模板中注入的样例数据(SampleUsers)实体类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class SampleUsers implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键自增ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 用户唯一标识（如 UUID）
     */
    private String creatorId;

    /**
     * 关联 sample_templates.sample_id
     */
    private String sampleId;

    /**
     * 用户看到的名称（默认继承模板 name，可自定义）
     */
    private String name;

    /**
     * 从模板中注入的配置数据（JSON 字符串，由 Java 序列化）
     */
    private String data;

    /**
     * 来源：system（系统自动注入）或 user（用户手动创建/修改）
     */
    private String source;

    /**
     * 注入时所用模板的版本号，用于后续升级判断
     */
    private String versionInjected;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createdTime;

    /**
     * 最后更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updatedTime;
}
