package com.iflytek.rpa.base.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 客户端版本检查DTO
 *
 * @author system
 * @since 2025-01-XX
 */
@Data
public class ClientVersionCheckDto {

    /**
     * 客户端当前版本号
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
}
