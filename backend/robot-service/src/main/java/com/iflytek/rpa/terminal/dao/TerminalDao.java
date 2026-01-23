package com.iflytek.rpa.terminal.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.terminal.entity.Terminal;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * @author mjren
 * @date 2025-06-10 16:53
 * @copyright Copyright (c) 2025 mjren
 */
@Mapper
public interface TerminalDao extends BaseMapper<Terminal> {

    Terminal getByTerminalId(@Param("terminalId") String terminalId);

    Integer updateByTerminalId(Terminal terminal);


    Integer updateStatusByTerminalIdList(@Param("terminalIdList") List<String> terminalIdList, @Param("status") String status);
}
