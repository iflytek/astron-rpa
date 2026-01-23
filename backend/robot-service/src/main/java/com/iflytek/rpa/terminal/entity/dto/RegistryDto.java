package com.iflytek.rpa.terminal.entity.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-06-16 15:09
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class RegistryDto {
    /**
     * 终端唯一标识，如设备mac地址
     */
    @NotBlank(message = "终端id不能为空")
    private String terminalId;

    /**
     * 终端名称
     */
    private String name;

    /**
     * 设备账号
     */
    private String account;

    /**
     * 操作系统
     */
    private String os;

    /**
     * 系统密码
     */
    private String osPwd;

    /**
     * IP地址
     */
    private String ip;

    /**
     * 端口
     */
    private Integer port;

    /**
     * 当前状态，用于计算最终状态，只有两种状态，运行中busy，空闲free
     */
    @NotBlank(message = "设备状态本能为空")
    private String status;

    /**
     * CPU占用率（百分比)
     */
    private Integer cpu;

    /**
     * 内存占用率（百分比)
     */
    private Integer memory;

    /**
     * 硬盘占用率（百分比)
     */
    private Integer disk;

    /**
     * 是否调度模式 (0: 否, 1: 是)
     */
    @NotNull(message = "终端模式不能为空")
    private Integer isDispatch;

    /**
     * 视频监控URL
     */
    private String monitorUrl;
}
