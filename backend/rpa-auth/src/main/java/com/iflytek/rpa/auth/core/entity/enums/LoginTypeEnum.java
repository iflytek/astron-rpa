package com.iflytek.rpa.auth.core.entity.enums;

import lombok.Getter;

@Getter
public enum LoginTypeEnum {
    /**
     * 验证码登录
     */
    CODE("code", "验证码登录"),
    /**
     * 密码登录
     */
    PASSWORD("password", "密码登录");

    private final String value;
    private final String name;

    LoginTypeEnum(String value, String name) {
        this.value = value;
        this.name = name;
    }
}
