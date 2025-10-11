package com.iflytek.rpa.monitor.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

@Data
public class RobotRecordVo {
    String executeId; // 执行id
    String robotId; // 机器人id
    String robotName; // 机器人名称
    String creatorId; // 所有者id
    String creatorName; // 所有者姓名

    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    String createTime; // 创建日期

    Long executeTotal; // 统计区间执行次数
    Long executeSuccess; // 统计区间执行成功次数
    Long executeTimeTotal; // 统计区间执行时长（小时）
}
