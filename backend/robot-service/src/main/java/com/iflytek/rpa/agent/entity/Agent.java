package com.iflytek.rpa.agent.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;
import lombok.experimental.Accessors;

/**
 * RPA Agent配置表实体类
 */
@Data
@Accessors(chain = true)
public class Agent implements Serializable {

    /**
     * 自增主键
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * RPA Agent ID
     */
    private String agentId;

    /**
     * Agent配置信息（超长文本）
     */
    private String content;

    /**
     * 删除标识：0-未删除，1-已删除
     */
    private Integer deleted;

    /**
     * 创建人ID
     */
    private String creatorId;

    /**
     * 创建时间，插入时自动生成
     */
    private Date createTime;

    /**
     * 更新人ID
     */
    private String updaterId;

    /**
     * 更新时间，更新时自动更新
     */
    private Date updateTime;
}
