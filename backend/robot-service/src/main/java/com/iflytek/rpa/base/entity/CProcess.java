package com.iflytek.rpa.base.entity;

import com.alibaba.fastjson.annotation.JSONField;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Null;
import lombok.Data;

/**
 * 流程项id数据(CProcess)实体类
 *
 * @author mjren
 * @since 2024-10-09 17:11:13
 */
@Data
public class CProcess implements Serializable {
    private static final long serialVersionUID = 533171820128533990L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 流程id
     */
    @Null
    @JSONField(name = "process_id")
    private String processId;
    /**
     * 全量流程数据
     */
    @Null
    @JSONField(name = "process_content")
    private String processContent;
    /**
     * 流程名称
     */
    @Null
    @JSONField(name = "process_name")
    private String processName;

    private Integer deleted;

    @JSONField(name = "creator_id")
    private String creatorId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    @JSONField(name = "updater_id")
    private String updaterId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    @NotBlank
    @JSONField(name = "robot_id")
    private String robotId;

    @NotBlank
    @JSONField(name = "robot_version")
    private Integer robotVersion;
}
