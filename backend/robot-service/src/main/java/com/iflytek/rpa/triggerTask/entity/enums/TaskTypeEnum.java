package com.iflytek.rpa.triggerTask.entity.enums;

import lombok.Getter;

/**
 * @author keler
 * @date 2021/10/9
 */
@Getter
public enum TaskTypeEnum {
    TIME_TASK("schedule", "时间"),
    FILE_TASK("file", "文件"),
    MAIL_TASK("mail", "邮箱"),
    HOT_KEY_TASK("hotKey", "热键触发"),
    MANUAL_TASK("manual", "热键触发"),
    ;

    private String code;
    private String name;

    TaskTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}
