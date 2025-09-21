package com.iflytek.rpa.component.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class CheckNameDto {

    @NotBlank(message = "组件新名称不能为空")
    String name;

    String componentId; // 组件id
}
