package com.iflytek.rpa.astronAgent.entity.dto;

import com.alibaba.fastjson.annotation.JSONField;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import java.util.List;
import lombok.Data;

/**
 * 复制机器人响应DTO
 */
@Data
public class CopyRobotResponseDto {

    /**
     * 复制后的机器人id
     */
    @JSONField(name = "robotId")
    private String robotId;

    /**
     * 机器人名称
     */
    private String name;

    /**
     * 英文名称
     */
    @JSONField(name = "english_name")
    private String englishName;

    /**
     * 描述
     */
    private String description;

    /**
     * 版本号
     */
    private String version;

    /**
     * 状态
     */
    private Integer status;

    /**
     * 参数列表
     */
    private List<ParamDto> parameters;
}
