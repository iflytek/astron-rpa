package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class EditCompUseDto {

    @NotBlank(message = "组件ID不能为空")
    String componentId;

    @NotBlank(message = "机器人ID不能为空")
    String robotId;

    @NotBlank(message = "运行位置不能为空")
    String mode; // 运行位置
}
