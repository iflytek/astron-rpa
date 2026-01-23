package com.iflytek.rpa.auth.auditRecord.entity.enums;

import static com.iflytek.rpa.auth.auditRecord.entity.enums.EventMoudleEnum.*;

import com.baomidou.mybatisplus.annotation.EnumValue;
import com.baomidou.mybatisplus.core.enums.IEnum;
import com.fasterxml.jackson.annotation.JsonCreator;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public enum EventTypeEnum implements IEnum<Integer> {

    /**
     * 创建角色
     */
    ADD_ROLE(1001, "创建角色", ROLE),

    /**
     * 重命名角色
     */
    RENAME_ROLE(1002, "重命名角色", ROLE),

    /**
     * 删除角色
     */
    DELETE_ROLE(1003, "删除角色", ROLE),

    /**
     * 添加成员
     */
    ADD_ROLE_USER(1004, "添加成员", ROLE),
    /**
     * 移除成员
     */
    REMOVE_ROLE_USER(1005, "移除成员", ROLE),
    /**
     * 编辑权限
     */
    EDIT_ROLE_FUNCTION(1006, "编辑权限", ROLE),
    /**
     * 删除机器人
     */
    REMOVE_ROBOT(1101, "删除机器人", ROBOT),
    /**
     * 转移机器人
     */
    TRANSFER_ROBOT(1102, "转移机器人", ROBOT),
    /**
     * 编辑权限
     */
    REMOVE_PROJECT(1201, "删除工程", PROJECT),
    /**
     * 编辑权限
     */
    TRANSFER_PROJECT(1202, "转移工程", PROJECT),

    /**
     * 新建任务
     */
    CREATE_TASK(1301, "新建任务", TASK),
    /**
     * 编辑任务
     */
    UPDATE_TASK(1302, "编辑任务", TASK),

    /**
     * 删除任务
     */
    REMOVE_TASK(1303, "删除任务", TASK),

    /**
     * 新建设备
     */
    CREATE_TERMINAL(1401, "新建设备", TERMINAL),
    /**
     * 编辑任务
     */
    REMOVE_TERMINAL(1402, "删除设备", TERMINAL),

    /**
     * 新建设备组
     */
    CREATE_TERMINAL_GROUP(1403, "新建设备组", TERMINAL),
    /**
     * 删除设备组
     */
    REMOVE_TERMINAL_GROUP(1404, "删除设备组", TERMINAL),
    ;

    EventTypeEnum(int code, String name) {
        this.code = code;
        this.name = name;
    }

    EventTypeEnum(int code, String name, EventMoudleEnum eventMoudleEnum) {
        this.code = code;
        this.name = name;
        this.eventMoudleEnum = eventMoudleEnum;
    }

    @EnumValue
    private final int code;

    private final String name;

    private EventMoudleEnum eventMoudleEnum;

    @JsonCreator
    public static EventTypeEnum getEnum(String name) {
        switch (name) {
            case "创建角色":
                return EventTypeEnum.ADD_ROLE;
            case "重命名角色":
                return EventTypeEnum.RENAME_ROLE;
            case "删除角色":
                return EventTypeEnum.DELETE_ROLE;
            case "添加成员":
                return EventTypeEnum.ADD_ROLE_USER;
            case "移除成员":
                return EventTypeEnum.REMOVE_ROLE_USER;
            case "编辑权限":
                return EventTypeEnum.EDIT_ROLE_FUNCTION;
            case "删除机器人":
                return EventTypeEnum.REMOVE_ROBOT;
            case "转移机器人":
                return EventTypeEnum.TRANSFER_ROBOT;
            case "删除工程":
                return EventTypeEnum.REMOVE_PROJECT;
            case "转移工程":
                return EventTypeEnum.TRANSFER_PROJECT;
            case "新建任务":
                return EventTypeEnum.CREATE_TASK;
            case "编辑任务":
                return EventTypeEnum.UPDATE_TASK;
            case "删除任务":
                return EventTypeEnum.REMOVE_TASK;
            case "新建设备":
                return EventTypeEnum.CREATE_TERMINAL;
            case "删除设备":
                return EventTypeEnum.REMOVE_TERMINAL;
            case "新建设备组":
                return EventTypeEnum.CREATE_TERMINAL_GROUP;
            case "删除设备组":
                return EventTypeEnum.REMOVE_TERMINAL_GROUP;
            default:
                return null;
        }
    }

    public static Map<Integer, String> eventTypeMap = new HashMap<>();
    public static List<Map<String, String>> eventTypeList = new ArrayList<>();

    static {
        initEventTypeMap();
        initEventTypeList();
    }

    public static void initEventTypeMap() {
        for (EventTypeEnum eventTypeEnum : EventTypeEnum.values()) {
            eventTypeMap.put(eventTypeEnum.getCode(), eventTypeEnum.getName());
        }
    }

    public static void initEventTypeList() {
        for (EventTypeEnum eventTypeEnum : EventTypeEnum.values()) {
            eventTypeList.add(new HashMap<String, String>() {
                {
                    put("typeCode", String.valueOf(eventTypeEnum.getCode()));
                    put("typeName", eventTypeEnum.getName());
                }
            });
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

    public EventMoudleEnum getEventMoudleEnum() {
        return eventMoudleEnum;
    }
}
