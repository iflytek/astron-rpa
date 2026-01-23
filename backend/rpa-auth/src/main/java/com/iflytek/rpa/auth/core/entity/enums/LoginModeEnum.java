package com.iflytek.rpa.auth.core.entity.enums;

/**
 * 登录模式枚举
 * @author lihang
 * @date 2025-11-25
 */
public enum LoginModeEnum {
    /**
     * 无密码登录
     */
    NOPASSWORD("NoPassword");

    private final String code;

    LoginModeEnum(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
