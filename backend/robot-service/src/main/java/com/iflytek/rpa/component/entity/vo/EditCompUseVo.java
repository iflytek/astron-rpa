package com.iflytek.rpa.component.entity.vo;

import lombok.Data;

@Data
public class EditCompUseVo {
    String componentId; // 组件id
    String name; // 组件名称
    Integer componentVersion; // 组件版本
    String icon; // 组件icon
}
