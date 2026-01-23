package com.iflytek.rpa.dispatch.entity.enums;

import lombok.Getter;

/**
 * 下发任务来源
 */
@Getter
public enum DispatchTaskFromType {
    NORMAL("normal", "普通"),
    RETRY("retry", "重试"),
    STOP("stop", "结束"),
    ;

    private final String value;
    private final String name;

    DispatchTaskFromType(String value, String name) {
        this.value = value;
        this.name = name;
    }
}
