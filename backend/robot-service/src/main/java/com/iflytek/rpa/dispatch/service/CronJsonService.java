package com.iflytek.rpa.dispatch.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.dispatch.entity.CronJson;
import java.text.ParseException;
import java.util.List;

public interface CronJsonService {
    /**
     * 根据cron配置计算未来执行时间
     *
     * @param cronJson cron配置JSON字符串
     * @return 未来执行时间列表
     * @throws JsonProcessingException JSON解析异常
     */
    List<String> getFutureList(String cronJson) throws Exception;

    List<String> calculateFutureExecuteTime(CronJson cron, Integer times) throws ParseException;
}
