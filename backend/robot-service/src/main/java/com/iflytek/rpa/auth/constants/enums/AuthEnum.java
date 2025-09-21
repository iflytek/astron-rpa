package com.iflytek.rpa.auth.constants.enums;

/**
 * @desc: 权限常量
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/19 9:49
 */
public enum AuthEnum {
    CASDOOR_CURRENT_USER_TOKEN("casdoor_current_user_token", "casdoor当前用户的token");

    private final String code;
    private final String description;

    AuthEnum(String code, String description) {
        this.code = code;
        this.description = description;
    }

    // 通过code获取枚举
    public static AuthEnum fromCode(String code) {
        for (AuthEnum ele : values()) {
            if (ele.code.equals(code)) {
                return ele;
            }
        }
        throw new IllegalArgumentException("未知权限编码: " + code);
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }
}
