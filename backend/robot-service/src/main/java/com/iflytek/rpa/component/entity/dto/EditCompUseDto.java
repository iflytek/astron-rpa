package com.iflytek.rpa.component.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class EditCompUseDto {

    @NotBlank(message = "组件ID不能为空")
    String componentId;

    @NotBlank(message = "机器人ID不能为空")
    String robotId;

    @NotBlank(message = "运行位置不能为空")
    String mode; // 运行位置
}
