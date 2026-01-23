package com.iflytek.rpa.market.entity.dto;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class PreReleaseCheckDto {
    /**
     * 机器人ID（必填）
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 机器人版本（必填）
     */
    @NotNull(message = "机器人版本不能为空")
    private Integer version;
}
