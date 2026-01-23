package com.iflytek.rpa.base.entity;

import com.alibaba.fastjson.annotation.JSONField;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 流程参数表
 *
 * @author tzzhang
 * @since
 */
@Data
public class CParam implements Serializable {
    private static final long serialVersionUID = -2745694034538081329L;

    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private String id;

    /**
     * 参数流向
     */
    @JSONField(name = "var_direction")
    private int varDirection;

    /**
     * 参数名称
     */
    @JSONField(name = "var_name")
    private String varName;

    /**
     * 参数类型
     */
    @JSONField(name = "var_type")
    private String varType;

    /**
     * 参数内容
     */
    @JSONField(name = "var_value")
    private String varValue;

    /**
     * 参数描述
     */
    @JSONField(name = "var_describe")
    private String varDescribe;

    /**
     * 流程id
     */
    @JSONField(name = "process_id")
    private String processId;

    @JSONField(name = "creator_id")
    private String creatorId;

    @JSONField(name = "updater_id")
    private String updaterId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    private Integer deleted;

    @JSONField(name = "robot_id")
    private String robotId;

    @JSONField(name = "robot_version")
    private Integer robotVersion;

    /**
     * 流程id
     */
    private String moduleId;
}
