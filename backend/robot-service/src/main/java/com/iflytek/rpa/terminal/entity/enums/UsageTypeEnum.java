package com.iflytek.rpa.terminal.entity.enums;

import lombok.Getter;

@Getter
public enum UsageTypeEnum {
    ALL("all", "所有人"),
    DEPT("dept", "所属部门所有人"),
    SELECT("select", "指定人"),
    ;

    private final String code;
    private final String name;

    UsageTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}
