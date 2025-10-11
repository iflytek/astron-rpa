package com.iflytek.rpa.monitor.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class RobotRecordDto {
    Integer pageSize = 8;

    Integer pageNo = 1;

    String sortBy = "executeTotal"; // 默认执行次数排序

    String sortType = "desc"; // 默认降序

    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date startTime; // 统计区间开始时间

    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date endTime; // 统计区间结束时间

    String robotId; // 机器人id

    String creatorId; // 创建人id

    String creatorName; // 创建人姓名

    String tenantId; // 租户id

    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date createTimeStart; // 创建时间起始

    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date createTimeEnd; // 创建时间结束

    List<String> deptIdPathList; // 部门id全路径列表

    String deptIdPath; // 部门id全路径

    private String deptId;
}
