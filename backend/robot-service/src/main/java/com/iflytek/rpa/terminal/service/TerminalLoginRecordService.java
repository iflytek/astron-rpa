package com.iflytek.rpa.terminal.service;

import com.iflytek.rpa.terminal.entity.TerminalLoginRecord;

/**
 * @author mjren
 * @date 2025-06-23 14:52
 * @copyright Copyright (c) 2025 mjren
 */
public interface TerminalLoginRecordService {
    Integer countUnLogoutRecordByTerminalId(String terminalId);

    Integer insertRecord(TerminalLoginRecord loginRecord);

    Integer setLogout(TerminalLoginRecord loginRecord);

    TerminalLoginRecord selectLogoutCandidates(String userId);
}
