package com.iflytek.rpa.base.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 客户端版本更新DTO
 *
 * @author system
 * @since 2025-01-XX
 */
@Data
public class ClientVersionUpdateDto {

    /**
     * 主键ID（更新时必填）
     */
    private Long id;

    /**
     * 版本号
     */
    @NotBlank(message = "版本号不能为空")
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
     * 下载链接
     */
    @NotBlank(message = "下载链接不能为空")
    private String downloadUrl;

    /**
     * 更新内容
     */
    private String updateInfo;
}
