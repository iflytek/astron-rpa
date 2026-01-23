package com.iflytek.rpa.base.entity.vo;

import java.io.Serializable;
import lombok.Data;

/**
 * 客户端版本检查VO
 *
 * @author system
 * @since 2025-01-XX
 */
@Data
public class ClientVersionCheckVo implements Serializable {

    /**
     * 是否需要更新：1-需要更新，0-不需要更新
     */
    private Integer needUpdate;

    /**
     * 最新版本号
     */
    private String version;

    /**
     * 更新信息
     */
    private String updateInfo;

    /**
     * 下载地址
     */
    private String downloadUrl;
    /**
     * 操作系统
     */
    private String os;

    /**
     * 架构
     */
    private String arch;
}
