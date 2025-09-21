package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

@Data
public class OpenModuleDto extends ProcessModuleListDto {
    String moduleId; // 模块Id

    @NotBlank(message = "运行位置不能为空")
    private String mode = EDIT_PAGE;
}
