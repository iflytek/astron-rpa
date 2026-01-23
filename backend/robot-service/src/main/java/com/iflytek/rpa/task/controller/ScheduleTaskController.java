package com.iflytek.rpa.task.controller;

import com.iflytek.rpa.task.entity.ScheduleTask;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskDto;
import com.iflytek.rpa.task.entity.dto.TaskDto;
import com.iflytek.rpa.task.service.ScheduleTaskService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 计划任务(ScheduleTask)表控制层
 *
 * @author makejava
 * @since 2024-09-29 15:27:42
 */
@RestController
@RequestMapping("/task")
public class ScheduleTaskController {
    /**
     * 服务对象
     */
    @Resource
    private ScheduleTaskService scheduleTaskService;

    /**
     * 计划任务列表查询
     * @param taskDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/list")
    public AppResponse<?> cloudTaskList(@RequestBody TaskDto taskDto) throws NoLoginException {
        return scheduleTaskService.getTaskList(taskDto);
    }

    /**
     * 保存/更新计划任务
     * @param task
     * @return
     * @throws Exception
     */
    @PostMapping("/save")
    public AppResponse<?> saveTask(@Valid @RequestBody ScheduleTaskDto task) throws Exception {
        return scheduleTaskService.saveTask(task);
    }

    /**
     * 计划任务详细信息
     * @return
     */
    @PostMapping("/task-info")
    public AppResponse<?> getTaskInfoByTaskId(@RequestBody ScheduleTaskDto task) throws NoLoginException {
        return scheduleTaskService.getTaskInfoByTaskId(task.getTaskId());
    }

    /**
     * 获取计划任务下次执行时间及机器人信息
     * @param
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/next-time")
    public AppResponse<?> getNextTimeInfo() throws NoLoginException {
        return scheduleTaskService.getNextTimeInfoAndUpdate();
    }

    /**
     * 计划任务-启用、禁用
     * @param
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/enable")
    public AppResponse<?> enableTask(@RequestBody ScheduleTask task) throws NoLoginException {
        return scheduleTaskService.enableTask(task);
    }

    /**
     * 计划任务-删除
     * @param task
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/delete")
    public AppResponse<?> deleteTask(@RequestBody ScheduleTask task) throws NoLoginException {
        return scheduleTaskService.deleteTask(task);
    }

    /**
     * 计划任务-重命名校验
     * @param task
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/name/same")
    public AppResponse<?> checkSameName(@RequestBody ScheduleTask task) throws NoLoginException {
        return scheduleTaskService.checkSameName(task);
    }

    /**
     * 计划任务-corn表达式校验
     * @param task
     * @return true 表示校验通过，false表示校验不通过
     * @throws NoLoginException
     */
    @PostMapping("/corn/check")
    public AppResponse<?> checkCorn(@RequestBody ScheduleTask task) throws NoLoginException {
        return scheduleTaskService.checkCorn(task);
    }
}
