package com.iflytek.rpa.terminal.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.terminal.entity.TerminalLoginRecord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * @author jqfang3
 * @date 2025-06-17
 */
@Mapper
public interface TerminalLoginRecordDao extends BaseMapper<TerminalLoginRecord> {

    Integer countUnLogoutRecordByTerminalId(@Param("terminalId") String terminalId);

    Integer setLogout(TerminalLoginRecord loginRecord);

    TerminalLoginRecord selectLogoutCandidates(@Param("userId") String userId);
}
