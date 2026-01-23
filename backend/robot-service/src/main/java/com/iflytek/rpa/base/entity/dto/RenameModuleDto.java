package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

@Data
public class RenameModuleDto extends ProcessModuleListDto {
    String moduleName; // 模块名称
    String moduleId; // 模块Id
}
