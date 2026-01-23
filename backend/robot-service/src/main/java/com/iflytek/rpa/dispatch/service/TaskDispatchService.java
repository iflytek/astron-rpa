package com.iflytek.rpa.dispatch.service;

import com.iflytek.rpa.dispatch.entity.TaskDispatchEvent;
import com.iflytek.rpa.dispatch.entity.dto.TaskDispatchDto;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskFromType;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskType;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

/**
 * 事件发布服务
 * 演示手动发布事件和注解自动发布事件
 */
@Slf4j
@Service
public class TaskDispatchService {

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    /**
     * 手动发布任务分派事件
     */
    public void dispatchTask(TaskDispatchDto taskDispatchDto) {
        log.info("手动发布任务分派事件: {}", taskDispatchDto);

        DispatchTaskType dispatchTaskType = DispatchTaskType.valueOf(taskDispatchDto.getDispatchTaskType());
        DispatchTaskFromType dispatchTaskFromType =
                DispatchTaskFromType.valueOf(taskDispatchDto.getDispatchTaskFromType());

        TaskDispatchEvent taskDispatchEvent = new TaskDispatchEvent(
                this,
                taskDispatchDto.getDispatchTaskId(),
                dispatchTaskType,
                dispatchTaskFromType,
                taskDispatchDto.getTerminalIds());

        // 手动发布事件
        eventPublisher.publishEvent(taskDispatchEvent);
    }
}
