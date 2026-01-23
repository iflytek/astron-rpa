package com.iflytek.rpa.terminal.constants;

/**
 * @author mjren
 * @date 2025-06-16 16:46
 * @copyright Copyright (c) 2025 mjren
 */
public class TerminalConstant {

    public static final String TERMINAL_NOT_FOUND = "TERMINAL_NOT_FOUND";

    /**
     * 设备状态，运行中busy，空闲free，离线offline，单机中standalone
     */
    public static final String TERMINAL_STATUS_BUSY = "busy";

    public static final String TERMINAL_STATUS_FREE = "free";

    public static final String TERMINAL_STATUS_OFFLINE = "offline";

    public static final String TERMINAL_STATUS_STANDALONE = "standalone";

    /**
     * redis key
     */
    public static final String TERMINAL_KEY_REAL_TIME = "terminalManage:realTime:";

    public static final String TERMINAL_KEY_STATUS = "terminalManage:onlineStatus";
}
