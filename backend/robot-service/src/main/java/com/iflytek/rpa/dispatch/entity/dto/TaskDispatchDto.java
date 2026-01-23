package com.iflytek.rpa.dispatch.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotEmpty;
import lombok.Data;

@Data
public class TaskDispatchDto {
    @NotBlank(message = "任务分派ID不能为空")
    private String dispatchTaskId;

    @NotEmpty(message = "终端不能为空")
    private List<String> terminalIds;

    private String dispatchTaskType;

    private String dispatchTaskFromType;
}
