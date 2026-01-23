package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class CSmartComponent implements Serializable {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 智能组件Id
     */
    private String smartId;

    /**
     * 组件类型 web_auto | data_process
     */
    private String smartType;

    /**
     * 机器人Id
     */
    private String robotId;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 组件内容
     */
    private String content;

    private Integer deleted;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;
}
