package com.iflytek.rpa.triggerTask.entity.enums;

import lombok.Getter;

@Getter
public enum ExceptionalEnum {
    JUMP("jump", "跳过"),
    STOP("stop", "中止"),
    RETRY_JUMP("retry_jump", "重试后跳过"),
    RETRY_STOP("retry_stop", "重试后停止"),
    ;

    private String code;
    private String name;

    ExceptionalEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}
