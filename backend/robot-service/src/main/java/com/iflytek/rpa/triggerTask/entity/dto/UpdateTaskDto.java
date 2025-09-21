package com.iflytek.rpa.triggerTask.entity.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

@Data
public class UpdateTaskDto extends InsertTaskDto {
    /**
     * 触发器计划任务id
     */
    @NotBlank
    String taskId;
}
