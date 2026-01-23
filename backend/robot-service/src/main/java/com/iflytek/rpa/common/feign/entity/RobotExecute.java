package com.iflytek.rpa.common.feign.entity;

import com.alibaba.fastjson.annotation.JSONField;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 云端机器人表(RobotExecute)实体类 - 用于Feign传输
 *
 * @author system
 */
@Data
public class RobotExecute implements Serializable {
    private static final long serialVersionUID = -49733269650418210L;
    /**
     * 主键id
     */
    private Long id;
    /**
     * 机器人唯一id，获取的应用id
     */
    @JSONField(name = "robot_id")
    private String robotId;
    /**
     * 当前名字，用于列表展示
     */
    private String name;
    /**
     * 创建者id
     */
    @JSONField(name = "creator_id")
    private String creatorId;
    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;
    /**
     * 更新者id
     */
    @JSONField(name = "updater_id")
    private String updaterId;
    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

    @JSONField(name = "tenant_id")
    private String tenantId;
    /**
     * appmarketResource中的应用id
     */
    @JSONField(name = "app_id")
    private String appId;
    /**
     * 获取的应用：应用市场版本
     */
    @JSONField(name = "app_version")
    private Integer appVersion;
    /**
     * 获取的应用：市场id
     */
    @JSONField(name = "market_id")
    private String marketId;
    /**
     * 资源状态：toObtain, obtaining, obtained, toUpdate, updating
     */
    @JSONField(name = "resource_status")
    private String resourceStatus;
    /**
     * 来源：create 自己创建 ； market 市场获取
     */
    @JSONField(name = "data_source")
    private String dataSource;

    @JSONField(name = "param_detail")
    private String paramDetail;

    /**
     * 部门id路径，用于根据部门统计机器人数量
     */
    @JSONField(name = "dept_id_path")
    private String deptIdPath;

    private Boolean isCreator;

    /**
     * 最新版本机器人的类型，web，other
     */
    private String type;

    /**
     * 最新版本 发版时间
     */
    @JSONField(name = "latest_release_time")
    private Date latestReleaseTime;

    @JSONField(name = "robot_version")
    private Integer robotVersion;

    private String introduction;
}
