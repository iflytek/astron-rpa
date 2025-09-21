package com.iflytek.rpa.utils;

public class RedisKeyUtils {
    private static final String prefix = "dispatch_task_";

    public static String getDispatchTaskListKey(String terminalId) {
        return prefix + terminalId.replace(":", "_") + "_list";
    }

    public static String getDispatchTaskStatusKey(String terminalId) {
        return prefix + terminalId.replace(":", "_") + "_flag";
    }
}
