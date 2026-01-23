package com.iflytek.rpa.dispatch.entity.enums;

import lombok.Getter;

/**
 * 终端或终端分组枚举
 *
 * @author jqfang
 * @since 2025-08-15
 */
@Getter
public enum TerminalOrGroupType {
    TERMINAL("terminal", "终端"),
    GROUP("group", "终端分组"),
    ;

    private final String value;
    private final String name;

    TerminalOrGroupType(String value, String name) {
        this.value = value;
        this.name = name;
    }
}
