package com.iflytek.rpa.feedback.entity.enums;

import lombok.Getter;

/**
 * 咨询表单状态枚举
 *
 * @author system
 * @since 2024-12-15
 */
@Getter
public enum FormStatus {
    PENDING(0, "待处理"),
    DONE(1, "已处理"),
    IGNORE(2, "已忽略");

    private final Integer code;
    private final String name;

    FormStatus(Integer code, String name) {
        this.code = code;
        this.name = name;
    }

    /**
     * 根据code获取枚举
     *
     * @param code 状态代码
     * @return 枚举值，如果不存在返回null
     */
    public static FormStatus getByCode(Integer code) {
        if (code == null) {
            return null;
        }
        for (FormStatus status : values()) {
            if (status.getCode().equals(code)) {
                return status;
            }
        }
        return null;
    }
}
