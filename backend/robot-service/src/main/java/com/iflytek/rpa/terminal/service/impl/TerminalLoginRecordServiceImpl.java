package com.iflytek.rpa.terminal.service.impl;

import com.iflytek.rpa.terminal.dao.TerminalLoginRecordDao;
import com.iflytek.rpa.terminal.entity.TerminalLoginRecord;
import com.iflytek.rpa.terminal.service.TerminalLoginRecordService;
import com.iflytek.rpa.utils.exception.ServiceException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * @author mjren
 * @date 2025-06-23 14:54
 * @copyright Copyright (c) 2025 mjren
 */
@Slf4j
@Service
public class TerminalLoginRecordServiceImpl implements TerminalLoginRecordService {

    @Autowired
    private TerminalLoginRecordDao terminalLoginRecordDao;

    @Override
    public Integer countUnLogoutRecordByTerminalId(String terminalId) {
        if (StringUtils.isBlank(terminalId)) {
            return 0;
        }
        return terminalLoginRecordDao.countUnLogoutRecordByTerminalId(terminalId);
    }

    @Override
    public Integer insertRecord(TerminalLoginRecord loginRecord) {
        if (null == loginRecord) {
            return 0;
        }
        return terminalLoginRecordDao.insert(loginRecord);
    }

    @Override
    public Integer setLogout(TerminalLoginRecord loginRecord) {
        return terminalLoginRecordDao.setLogout(loginRecord);
    }

    @Override
    public TerminalLoginRecord selectLogoutCandidates(String userId) {
        if (StringUtils.isBlank(userId)) {
            throw new ServiceException("无法获取用户id");
        }
        return terminalLoginRecordDao.selectLogoutCandidates(userId);
    }
}
