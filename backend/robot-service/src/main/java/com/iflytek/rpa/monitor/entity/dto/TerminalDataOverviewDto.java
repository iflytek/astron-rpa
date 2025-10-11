package com.iflytek.rpa.monitor.entity.dto;

import lombok.Data;

@Data
public class TerminalDataOverviewDto {
    /**
     * 执行成功次数
     */
    private Long terminalNum = 0L;

    /**
     * 执行时长
     */
    private String terminalTimeHour;
}
