package com.iflytek.rpa.dispatch.entity.enums;

import lombok.Getter;

/**
 * 调度任务类型枚举
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Getter
public enum DispatchTaskType {
    MANUAL("manual", "手动触发"),
    SCHEDULE("schedule", "定时"),
    TRIGGER("trigger", "定时触发"),
    ;

    private final String value;
    private final String name;

    DispatchTaskType(String value, String name) {
        this.value = value;
        this.name = name;
    }
    // 添加根据value值获取枚举的方法
    public static DispatchTaskType getByValue(String value) {
        for (DispatchTaskType type : values()) {
            if (type.getValue().equals(value)) {
                return type;
            }
        }
        throw new IllegalArgumentException("未知的任务类型: " + value);
    }
}
