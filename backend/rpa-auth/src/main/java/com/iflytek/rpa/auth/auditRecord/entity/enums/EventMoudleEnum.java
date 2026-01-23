package com.iflytek.rpa.auth.auditRecord.entity.enums;

import com.baomidou.mybatisplus.annotation.EnumValue;
import com.baomidou.mybatisplus.core.enums.IEnum;
import com.fasterxml.jackson.annotation.JsonCreator;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public enum EventMoudleEnum implements IEnum<Integer> {

    /**
     * 管理员权限
     */
    ROLE(10, "管理员权限"),
    ROBOT(11, "机器人管理"),
    PROJECT(12, "工程管理"),
    TASK(13, "任务管理"),
    TERMINAL(14, "终端管理"),
    ;

    EventMoudleEnum(int code, String name) {
        this.code = code;
        this.name = name;
    }

    @EnumValue
    private final int code;

    private final String name;

    public static Map<Integer, String> eventModuleMap = new HashMap<>();
    public static List<Map<String, String>> eventModuleList = new ArrayList<>();

    static {
        initEventModuleMap();
        initEventModuleList();
    }

    public static void initEventModuleMap() {
        for (EventMoudleEnum eventMoudleEnum : EventMoudleEnum.values()) {
            eventModuleMap.put(eventMoudleEnum.getCode(), eventMoudleEnum.getName());
        }
    }

    public static void initEventModuleList() {
        for (EventMoudleEnum eventMoudleEnum : EventMoudleEnum.values()) {
            eventModuleList.add(new HashMap<String, String>() {
                {
                    put("typeCode", String.valueOf(eventMoudleEnum.getCode()));
                    put("typeName", eventMoudleEnum.getName());
                }
            });
        }
    }

    @JsonCreator
    public static EventMoudleEnum getEnum(String name) {
        switch (name) {
            case "管理员权限":
                return EventMoudleEnum.ROLE;
            case "机器人管理":
                return EventMoudleEnum.ROBOT;
            case "工程管理":
                return EventMoudleEnum.PROJECT;
            case "任务管理":
                return EventMoudleEnum.TASK;
            case "终端管理":
                return EventMoudleEnum.TERMINAL;
            default:
                return null;
        }
    }

    @Override
    public Integer getValue() {
        return code;
    }

    public Integer getCode() {
        return code;
    }

    public String getName() {
        return name;
    }
}
