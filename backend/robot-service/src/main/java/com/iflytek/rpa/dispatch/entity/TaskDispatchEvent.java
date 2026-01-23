package com.iflytek.rpa.dispatch.entity;

import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskFromType;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskType;
import java.util.List;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import org.springframework.context.ApplicationEvent;

/**
 * 任务调度事件
 */
@Getter
@Setter
@EqualsAndHashCode(callSuper = true)
public class TaskDispatchEvent extends ApplicationEvent {

    private String dispatchTaskId;
    private DispatchTaskType dispatchTaskType;
    private DispatchTaskFromType dispatchTaskFromType;
    private List<String> dispatchTerminalIds;

    public TaskDispatchEvent(
            Object source,
            String dispatchTaskId,
            DispatchTaskType dispatchTaskType,
            DispatchTaskFromType dispatchTaskFromType,
            List<String> dispatchTerminalIds) {
        super(source);
        this.dispatchTaskId = dispatchTaskId;
        this.dispatchTaskType = dispatchTaskType;
        this.dispatchTaskFromType = dispatchTaskFromType;
        this.dispatchTerminalIds = dispatchTerminalIds;
    }
}
