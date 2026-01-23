package com.iflytek.rpa.task.entity.dto;

import lombok.Data;

import java.util.List;

@Data
public class ScheduleTaskRecordDeleteDto {
    List<String> taskExecuteIdList;
}
