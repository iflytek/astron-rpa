package com.iflytek.rpa.auth.idp.iflytekIdentity.enums;

import lombok.Getter;

@Getter
public enum IflytekLoginModeEnum {
    PASSWORD("phone", "手机号密码登录"),
    FREE("free", "无密码登录");

    private final String value;
    private final String name;

    IflytekLoginModeEnum(String value, String name) {
        this.value = value;
        this.name = name;
    }
}
