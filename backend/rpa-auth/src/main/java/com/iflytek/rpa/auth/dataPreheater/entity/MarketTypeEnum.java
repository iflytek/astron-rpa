package com.iflytek.rpa.auth.dataPreheater.entity;

import lombok.Getter;

@Getter
public enum MarketTypeEnum {
    TEAM("team", "团队市场"),
    OFFICIAL("official", "官方市场"),
    PUBLIC("public", "企业公共市场"),
    ;

    private final String code;
    private final String name;

    MarketTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}
