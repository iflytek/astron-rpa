package com.iflytek.rpa.dispatch.service.impl;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.dispatch.entity.CronJson;
import com.iflytek.rpa.dispatch.service.CronJsonService;
import com.iflytek.rpa.task.service.CronExpression;
import com.iflytek.rpa.utils.DateUtils;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service("CronJsonService")
public class CronJsonServiceImpl implements CronJsonService {
    @Override
    public List<String> getFutureList(String cronJson) throws Exception {
        if (null == cronJson || cronJson.isEmpty()) {
            return Collections.emptyList();
        }
        ObjectMapper mapper = new ObjectMapper();
        CronJson object = mapper.readValue(cronJson, CronJson.class);
        Integer times = Integer.valueOf(object.getTimes());
        if (times <= 0) {
            times = 5;
        }
        // 使用解析出的CronJson对象计算执行时间
        return calculateFutureExecuteTime(object, times);
    }

    @Override
    public List<String> calculateFutureExecuteTime(CronJson cron, Integer times) throws ParseException {
        List<String> futureExecTimes = new ArrayList<>();
        // 生成cron表达式
        String cronExpression = generateCronExpression(cron);
        if (cronExpression == null) {
            return futureExecTimes;
        }

        // 解析结束时间（如果存在）
        Date endTime = null;
        String endTimeStr = cron.getEndTime();
        // 如果结束时间不为空，则解析为Date对象
        if (endTimeStr != null && !endTimeStr.trim().isEmpty()) {
            endTime = DateUtils.sdfdaytime.parse(endTimeStr);
        }
        // 创建CronExpression对象
        CronExpression cronExpr = new CronExpression(cronExpression);
        // 从当前时间开始计算
        Date nextRun = new Date();
        // 计算 5次
        // 计算未来N次执行时间
        for (int i = 0; i < times; i++) {
            nextRun = cronExpr.getNextValidTimeAfter(nextRun);
            if (nextRun == null) {
                break;
            }
            // 超过定时结束时间，停止计算
            if (endTime != null && nextRun.after(endTime)) {
                break;
            }
            futureExecTimes.add(DateUtils.sdfdaytime.format(nextRun));
        }
        return futureExecTimes;
    }

    /**
     * 根据不同的频率类型生成cron表达式
     */
    private String generateCronExpression(CronJson cron) {
        String frequencyFlag = cron.getFrequencyFlag();

        if (frequencyFlag == null) {
            return null;
        }

        switch (frequencyFlag.toLowerCase()) {
            case "regular":
                return generateRegularCron(cron.getTimeExpression());
            case "minutes":
                return generateMinutesCron(cron.getMinutes());
            case "hours":
                return generateHoursCron(cron.getMinutes(), cron.getHours());
            case "days":
                return generateDaysCron(cron.getMinutes(), cron.getHours());
            case "weeks":
                return generateWeeksCron(cron.getMinutes(), cron.getHours(), cron.getWeeks());
            case "months":
                return generateMonthsCron(cron.getMinutes(), cron.getHours(), cron.getWeeks(), cron.getMonths());
            case "advance":
                return cron.getCronExpression();
            default:
                throw new IllegalArgumentException("不支持的频率类型: " + frequencyFlag);
        }
    }

    /**
     * 生成定时执行的cron表达式 (regular类型)
     */
    private String generateRegularCron(String timeExpression) {
        if (timeExpression == null) {
            return null;
        }
        // 解析时间表达式
        String[] parts = timeExpression.split(" ");
        if (parts.length != 2) {
            return null;
        }
        String[] dateParts = parts[0].split("-");
        String[] timeParts = parts[1].split(":");
        if (dateParts.length != 3 || timeParts.length != 3) {
            return null;
        }
        String second = timeParts[2];
        String minute = timeParts[1];
        String hour = timeParts[0];
        String day = dateParts[2];
        String month = dateParts[1];
        String year = dateParts[0];
        // Spring的cron表达式格式：秒 分 时 日 月 周 [年]
        return String.format("%s %s %s %s %s ? %s", second, minute, hour, day, month, year);
    }

    /**
     * 生成按分钟间隔执行的cron表达式
     */
    private String generateMinutesCron(Integer minutes) {
        if (minutes == null || minutes < 1 || minutes >= 60) {
            throw new IllegalArgumentException("分钟间隔必须在1-59之间");
        }
        // 每N分钟执行一次
        return String.format("0 0/%d * * * ?", minutes);
    }

    /**
     * 生成按小时间隔执行的cron表达式
     */
    private String generateHoursCron(Integer minutes, Integer hours) {
        if (minutes == null || hours == null) {
            throw new IllegalArgumentException("分钟和小时不能为空");
        }
        if (minutes < 0 || minutes >= 60) {
            throw new IllegalArgumentException("分钟必须在0-59之间");
        }
        if (hours < 1 || hours > 24) {
            throw new IllegalArgumentException("小时间隔必须在1-24之间");
        }
        // 每N小时的第M分钟执行
        return String.format("0 %d 0/%d * * ?", minutes, hours);
    }

    /**
     * 生成每天执行的cron表达式
     */
    private String generateDaysCron(Integer minutes, Integer hours) {
        if (minutes == null || hours == null) {
            throw new IllegalArgumentException("分钟和小时不能为空");
        }
        if (minutes < 0 || minutes >= 60) {
            throw new IllegalArgumentException("分钟必须在0-59之间");
        }
        if (hours < 0 || hours >= 24) {
            throw new IllegalArgumentException("小时必须在0-23之间");
        }
        // 每天的指定时间执行
        return String.format("0 %d %d * * ?", minutes, hours);
    }

    /**
     * 生成按周执行的cron表达式
     */
    private String generateWeeksCron(Integer minutes, Integer hours, List<Integer> weeks) {
        if (minutes == null || hours == null || weeks == null || weeks.isEmpty()) {
            throw new IllegalArgumentException("分钟、小时和星期不能为空");
        }
        if (minutes < 0 || minutes >= 60) {
            throw new IllegalArgumentException("分钟必须在0-59之间");
        }
        if (hours < 0 || hours >= 24) {
            throw new IllegalArgumentException("小时必须在0-23之间");
        }
        // 验证星期值 (0=周日, 1=周一, ... 6=周六)
        for (Integer week : weeks) {
            if (week < 0 || week > 6) {
                throw new IllegalArgumentException("星期必须在0-6之间");
            }
        }
        // 转换为Spring cron格式的星期 (1=周日, 2=周一, ... 7=周六)
        List<String> springWeeks = new ArrayList<>();
        for (Integer week : weeks) {
            springWeeks.add(String.valueOf(week + 2));
        }
        String weekExpression = String.join(",", springWeeks);
        return String.format("0 %d %d ? * %s", minutes, hours, weekExpression);
    }

    /**
     * 生成按月执行的cron表达式
     */
    private String generateMonthsCron(Integer minutes, Integer hours, List<Integer> weeks, List<Integer> months) {
        if (minutes == null
                || hours == null
                || weeks == null
                || months == null
                || weeks.isEmpty()
                || months.isEmpty()) {
            throw new IllegalArgumentException("分钟、小时、星期和月份不能为空");
        }
        if (minutes < 0 || minutes >= 60) {
            throw new IllegalArgumentException("分钟必须在0-59之间");
        }
        if (hours < 0 || hours >= 24) {
            throw new IllegalArgumentException("小时必须在0-23之间");
        }
        // 验证星期值
        for (Integer week : weeks) {
            if (week < 0 || week > 6) {
                throw new IllegalArgumentException("星期必须在0-6之间");
            }
        }
        // 验证月份值
        for (Integer month : months) {
            if (month < 1 || month > 12) {
                throw new IllegalArgumentException("月份必须在1-12之间");
            }
        }
        // 转换星期格式
        List<String> springWeeks = new ArrayList<>();
        // 转换为Spring cron格式的星期 (1=周日, 2=周一, ... 7=周六)
        for (Integer week : weeks) {
            springWeeks.add(String.valueOf(week + 2));
        }
        String weekExpression = String.join(",", springWeeks);
        String monthExpression = months.stream()
                .map(String::valueOf)
                .reduce((a, b) -> a + "," + b)
                .orElse("");
        return String.format("0 %d %d ? %s %s", minutes, hours, monthExpression, weekExpression);
    }
}
