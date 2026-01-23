package com.iflytek.rpa.base.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 客户端版本更新VO
 *
 * @author system
 * @since 2025-01-XX
 */
@Data
public class ClientVersionUpdateVo implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键ID
     */
    private Long id;

    /**
     * 版本号
     */
    private String version;

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
     * 操作系统
     */
    private String os;

    /**
     * 架构
     */
    private String arch;

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
}
