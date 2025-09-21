package com.iflytek.rpa.triggerTask.entity.vo;

import lombok.Data;

@Data
public class Executor {
    String robotId;
    String robotName;
    Integer robotVersion;

    private Boolean haveParam;

    private String paramJson;
}
