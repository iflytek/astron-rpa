package com.iflytek.rpa.feedback.entity.enums;

import lombok.Getter;

/**
 * 咨询表单类型枚举
 *
 * @author system
 * @since 2024-12-15
 */
@Getter
public enum FormType {
    PRO(1, "专业版咨询"),
    ENTERPRISE(2, "企业版咨询");

    private final Integer code;
    private final String name;

    FormType(Integer code, String name) {
        this.code = code;
        this.name = name;
    }

    /**
     * 根据code获取枚举
     *
     * @param code 类型代码
     * @return 枚举值，如果不存在返回null
     */
    public static FormType getByCode(Integer code) {
        if (code == null) {
            return null;
        }
        for (FormType type : values()) {
            if (type.getCode().equals(code)) {
                return type;
            }
        }
        return null;
    }
}
