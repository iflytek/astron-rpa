package com.iflytek.rpa.monitor.entity.vo;

import cn.afterturn.easypoi.excel.annotation.Excel;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

@Data
public class RobotRecordExcelVo {
    @Excel(name = "机器人名称", orderNum = "1", width = 25)
    String robotName; // 机器人名称

    @Excel(name = "所有者姓名", orderNum = "2", width = 25)
    String creatorName; // 所有者姓名

    @Excel(name = "创建日期", orderNum = "3", width = 75)
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    String createTime; // 创建日期

    @Excel(name = "统计区间执行次数", orderNum = "4", width = 25)
    Long executeTotal; // 统计区间执行次数

    @Excel(name = "统计区间执行成功次数", orderNum = "5", width = 25)
    Long executeSuccess; // 统计区间执行成功次数

    @Excel(name = "统计区间执行时长（小时）", orderNum = "6", width = 25)
    Long executeTimeTotal; // 统计区间执行时长（小时）
}
