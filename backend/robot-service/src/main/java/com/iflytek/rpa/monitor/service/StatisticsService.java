package com.iflytek.rpa.monitor.service;

import java.util.Date;

/**
 * 统计服务
 *
 */
public interface StatisticsService {

    /**
     *
     * @param date 统计哪一天的数据
     */
    void statisticsRobotData(Date date);

    void statisticsBaseOnDept(Date date);

    void statisticsTerminalData(Date date);
}
