package com.iflytek.rpa.astronAgent.entity.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * 复制机器人请求DTO
 */
@Data
public class CopyRobotDto {

    /**
     * 机器人id（appId）
     */
    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    /**
     * 机器人版本
     */
    @NotNull(message = "机器人版本不能为空")
    private Integer version;

    /**
     * 目标账户手机号
     */
    @NotBlank(message = "目标账户手机号不能为空")
    private String targetPhone;
}
