package com.iflytek.rpa.dispatch.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CronJson {
    /**
     * 执行次数
     */
    @JsonProperty("times")
    private String times;
    /**
     * 结束时间，格式："2025-03-24 15:32:23"
     */
    @JsonProperty("end_time")
    private String endTime;

    /**
     * 频率标志，枚举值：regular、minutes、hours、days、weeks、months、advance
     */
    @JsonProperty("frequency_flag")
    private String frequencyFlag;

    /**
     * 分钟，范围：[0, 59]
     */
    @JsonProperty("minutes")
    private Integer minutes;

    /**
     * 小时，范围：[0, 23]
     */
    @JsonProperty("hours")
    private Integer hours;

    /**
     * 周，范围：[0, 6]，0表示周日
     */
    @JsonProperty("weeks")
    private List<Integer> weeks;

    /**
     * 月份，范围：[1, 12]
     */
    @JsonProperty("months")
    private List<Integer> months;

    /**
     * 时间表达式，格式："2025-03-24 15:32:23"
     */
    @JsonProperty("time_expression")
    private String timeExpression;

    /**
     * cron表达式，格式："* * * * *"
     */
    @JsonProperty("cron_expression")
    private String cronExpression;
}
