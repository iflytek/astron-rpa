package com.iflytek.rpa.component.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * 添加组件引用DTO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class DelComponentUseDto {

    /**
     * 运行位置
     */
    @NotBlank(message = "运行位置不能为空")
    private String mode;

    /**
     * 机器人ID
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 机器人版本
     */
    private Integer robotVersion;

    /**
     * 组件ID
     */
    @NotBlank(message = "组件ID不能为空")
    private String componentId;
}