package com.iflytek.rpa.triggerTask.entity.dto;

import lombok.Data;

@Data
public class TaskPageDto {
    Integer pageSize = 8;
    Integer pageNo = 1;
    String name; // 计划任务名称，模糊查询
    String taskType; // 定时:schedule、邮件mail、文件file、热键hotKey
}
