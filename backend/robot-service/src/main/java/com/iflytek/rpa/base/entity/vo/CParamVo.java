package com.iflytek.rpa.base.entity.vo;

import lombok.Data;

@Data
public class CParamVo {

    private String id;

    private int varDirection;

    private String varName;

    private String varType;

    private String varValue;

    private String varDescribe;

    private String robotId;

    private Integer robot_version;

    private String processId;
}
