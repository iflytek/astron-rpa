package com.iflytek.rpa.dispatch.listener;

import com.iflytek.rpa.dispatch.entity.RedisListBo;
import com.iflytek.rpa.dispatch.entity.TaskDispatchEvent;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskFromType;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskType;
import com.iflytek.rpa.utils.RedisKeyUtils;
import com.iflytek.rpa.utils.RedisUtils;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * 任务调度事件监听器
 */
@Slf4j
@Component
public class TaskDispatchEventListener {

    @EventListener
    public void handleTaskDispatched(TaskDispatchEvent event) {
        log.info("收到任务调度事件: {}", event);

        // 将事件信息存储到Redis中
        // 1、从计划任务列表里的变更
        //     a. 对于手动任务，触发方式只有通过运行按钮下发，因此添加到队列里去
        //     b. 对于定时和计划任务，因为是任何变动都需要下发，因此设置标识表示是否有变更
        // 2、从执行记录列表里的重试和结束
        //     a. 不分任务类型，可以将所有任务通过重试按钮直接丢到队列里去，参数从执行记录里取
        List<String> terminalIds = event.getDispatchTerminalIds();
        if (terminalIds != null && !terminalIds.isEmpty()) {
            if (event.getDispatchTaskFromType() == DispatchTaskFromType.NORMAL) {
                for (String terminalId : terminalIds) {
                    if (event.getDispatchTaskType() == DispatchTaskType.MANUAL) {
                        String redisKey = RedisKeyUtils.getDispatchTaskListKey(terminalId);
                        // 将dispatchTaskId添加到队列（list）中
                        RedisUtils.lSet(
                                redisKey, new RedisListBo(event.getDispatchTaskId(), event.getDispatchTaskFromType()));
                        log.info("已将手动任务调度事件的taskId添加到Redis队列: key={}, value={}", redisKey, event.getDispatchTaskId());
                    } else {
                        String redisKey = RedisKeyUtils.getDispatchTaskStatusKey(terminalId);
                        // 设置Redis key，value为"1"，永不过期
                        RedisUtils.set(redisKey, "1");
                        log.info("已将定时任务调度事件存储到Redis: key={}, value=1", redisKey);
                    }
                }
            } else {
                for (String terminalId : terminalIds) {
                    String redisKey = RedisKeyUtils.getDispatchTaskListKey(terminalId);
                    RedisUtils.lSet(
                            redisKey, new RedisListBo(event.getDispatchTaskId(), event.getDispatchTaskFromType()));
                    log.info("已将重试任务调度事件的taskId添加到Redis队列: key={}", redisKey);
                }
            }
        }
    }
}
