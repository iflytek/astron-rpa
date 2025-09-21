package com.iflytek.rpa.task.entity.enums;

import lombok.Getter;

/**
 * @author keler
 * @date 2021/10/9
 */
@Getter
public enum TerminalTypeEnum {
    PRIVATE("private", "个人"),
    PUBLIC("public", "公共"),
    ;

    private String code;
    private String name;

    TerminalTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}
