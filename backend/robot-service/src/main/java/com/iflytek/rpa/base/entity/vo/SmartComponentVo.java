package com.iflytek.rpa.base.entity.vo;

import com.iflytek.rpa.base.entity.dto.CSmartComponentDto;
import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class SmartComponentVo {
    /**
     * 智能组件Id
     */
    private String smartId;

    /**
     * 机器人Id
     */
    private String robotId;

    /**
     * 组件各版本详细内容
     */
    private CSmartComponentDto.SmartDetail detail;

    /**
     * 组件类型 web_auto | data_process
     */
    private String smartType;
}
