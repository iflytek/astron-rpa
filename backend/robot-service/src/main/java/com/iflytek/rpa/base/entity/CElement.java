package com.iflytek.rpa.base.entity;

import com.alibaba.fastjson.annotation.JSONField;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 客户端，元素信息(CElement)实体类
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Data
public class CElement implements Serializable {
    private static final long serialVersionUID = -53914169890628551L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 分组id
     */
    @JSONField(name = "group_id")
    private String groupId;

    /**
     * 元素拾取类型：sigle普通拾取，batch数据抓取
     */
    @JSONField(name = "common_sub_type")
    private String commonSubType;

    /**
     * 元素id
     */
    @JSONField(name = "element_id")
    private String elementId;
    /**
     * 元素名称
     */
    @JSONField(name = "element_name")
    private String elementName;
    /**
     * 图标
     */
    private String icon;
    /**
     * 图片下载id
     */
    @JSONField(name = "image_id")
    private String imageId;
    /**
     * 元素内容
     */
    @JSONField(name = "element_data")
    private String elementData;

    private Integer deleted;

    @JSONField(name = "creator_id")
    private String creatorId;

    private Date createTime;

    @JSONField(name = "updater_id")
    private String updaterId;

    private Date updateTime;
    /**
     * 元素的父级图片id
     */
    @JSONField(name = "parent_image_id")
    private String parentImageId;

    @JSONField(name = "robot_id")
    private String robotId;

    @JSONField(name = "robot_version")
    private Integer robotVersion;
}
