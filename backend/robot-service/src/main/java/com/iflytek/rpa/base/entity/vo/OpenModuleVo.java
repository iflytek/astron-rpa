package com.iflytek.rpa.base.entity.vo;

import com.iflytek.rpa.base.entity.dto.OpenModuleDto;
import lombok.Data;

@Data
public class OpenModuleVo extends OpenModuleDto {
    String moduleContent; // 代码内容
}
