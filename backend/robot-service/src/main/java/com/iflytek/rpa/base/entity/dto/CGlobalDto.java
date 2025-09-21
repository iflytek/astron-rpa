package com.iflytek.rpa.base.entity.dto;


import lombok.Data;

import javax.validation.constraints.NotBlank;


@Data
public class CGlobalDto {
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    private String globalId;
    private String varName;
    private String varType;
    private String varValue;
    private String varDescribe;
    private String creatorId;
    private String updaterId;
}
