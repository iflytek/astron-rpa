package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 客户端版本检查表(ClientUpdateVersion)实体类
 *
 * @author system
 * @since 2025-01-XX
 */
@Data
public class ClientUpdateVersion implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 版本号
     */
    private String version;

    /**
     * 操作系统
     */
    private String os;

    /**
     * 架构
     */
    private String arch;

    /**
     * 版本数字
     */
    private Integer versionNum;

    /**
     * 下载链接
     */
    private String downloadUrl;

    /**
     * 更新内容
     */
    private String updateInfo;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}
