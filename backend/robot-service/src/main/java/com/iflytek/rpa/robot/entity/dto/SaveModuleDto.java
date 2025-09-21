package com.iflytek.rpa.robot.entity.dto;

import com.iflytek.rpa.base.entity.dto.OpenModuleDto;
import lombok.Data;

@Data
public class SaveModuleDto extends OpenModuleDto {
    String moduleContent; // 代码模块内容
    String robotId; // robotID
}
