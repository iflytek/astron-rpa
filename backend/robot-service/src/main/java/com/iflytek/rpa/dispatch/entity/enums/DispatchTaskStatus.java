package com.iflytek.rpa.dispatch.entity.enums;

import lombok.Getter;

/**
 * 调度任务状态枚举
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Getter
public enum DispatchTaskStatus {
    ACTIVE("active", "启用中"),
    STOP("stop", "关闭"),
    EXPIRED("expired", "已过期"),
    ;

    private final String value;
    private final String name;

    DispatchTaskStatus(String value, String name) {
        this.value = value;
        this.name = name;
    }
}
