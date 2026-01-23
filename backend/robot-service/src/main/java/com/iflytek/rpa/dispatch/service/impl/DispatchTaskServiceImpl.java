package com.iflytek.rpa.dispatch.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.dispatch.dao.DispatchTaskDao;
import com.iflytek.rpa.dispatch.entity.CronJson;
import com.iflytek.rpa.dispatch.entity.DispatchTask;
import com.iflytek.rpa.dispatch.entity.RedisListBo;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskFromType;
import com.iflytek.rpa.dispatch.entity.enums.DispatchTaskStatus;
import com.iflytek.rpa.dispatch.entity.vo.TerminalTaskDetailVo;
import com.iflytek.rpa.dispatch.service.DispatchTaskService;
import com.iflytek.rpa.utils.DateUtils;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.RedisKeyUtils;
import com.iflytek.rpa.utils.RedisUtils;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

@Service("dispatchTaskService")
@Slf4j
public class DispatchTaskServiceImpl extends ServiceImpl<DispatchTaskDao, DispatchTask> implements DispatchTaskService {
    @Autowired
    private DispatchTaskDao dispatchTaskDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private ApplicationEventPublisher eventPublisher;

    @Autowired
    private DispatchTaskService self; // 自注入

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    /**
     * 检查并更新任务过期状态
     * 只处理active和expired状态的任务，根据time_expression进行状态转换
     *
     * @param tasks 任务列表
     */
    private void checkAndUpdateTaskExpiredStatus(List<DispatchTask> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return;
        }

        Date currentTime = new Date();
        List<DispatchTask> tasksToUpdate = new ArrayList<>();

        for (DispatchTask task : tasks) {
            // 只处理active和expired状态的任务
            if (!DispatchTaskStatus.ACTIVE.getValue().equals(task.getStatus())
                    && !DispatchTaskStatus.EXPIRED.getValue().equals(task.getStatus())) {
                continue;
            }

            // 检查cronJson中是否有time_expression
            if (task.getCronJson() != null && !task.getCronJson().trim().isEmpty()) {
                try {
                    ObjectMapper objectMapper = new ObjectMapper();
                    CronJson cronJson = objectMapper.readValue(task.getCronJson(), CronJson.class);

                    // 如果有end_time且不为空
                    if (cronJson.getEndTime() != null
                            && !cronJson.getEndTime().trim().isEmpty()) {
                        // 解析时间表达式
                        Date taskEndTime = DateUtils.sdfdaytime.parse(cronJson.getEndTime());

                        String currentStatus = task.getStatus();
                        String newStatus = null;

                        // 判断当前状态和过期状态，决定是否需要更新
                        if (DispatchTaskStatus.ACTIVE.getValue().equals(currentStatus)) {
                            // 如果当前是active状态，但时间已过期，则更新为expired
                            if (taskEndTime.before(currentTime)) {
                                newStatus = DispatchTaskStatus.EXPIRED.getValue();
                                log.info(
                                        "任务{}从active更新为expired，结束时间：{}，当前时间：{}",
                                        task.getDispatchTaskId(),
                                        cronJson.getTimeExpression(),
                                        DateUtils.getDayTimeFormat(currentTime));
                            }
                        } else if (DispatchTaskStatus.EXPIRED.getValue().equals(currentStatus)) {
                            // 如果当前是expired状态，但时间还未过期，则更新为active
                            if (taskEndTime.after(currentTime) || taskEndTime.equals(currentTime)) {
                                newStatus = DispatchTaskStatus.ACTIVE.getValue();
                                log.info(
                                        "任务{}从expired更新为active，结束时间：{}，当前时间：{}",
                                        task.getDispatchTaskId(),
                                        cronJson.getTimeExpression(),
                                        DateUtils.getDayTimeFormat(currentTime));
                            }
                        }

                        // 如果需要更新状态
                        if (newStatus != null) {
                            task.setStatus(newStatus);
                            task.setUpdateTime(currentTime);
                            tasksToUpdate.add(task);
                        }
                    } else if (DispatchTaskStatus.EXPIRED.getValue().equals(task.getStatus())) {
                        // 如果当前是expired状态，但是没有配置cron_json,则保持ac状态
                        task.setStatus(DispatchTaskStatus.ACTIVE.getValue());
                        task.setUpdateTime(currentTime);
                        tasksToUpdate.add(task);
                    }
                } catch (Exception e) {
                    log.error("解析任务{}的cronJson失败：{}", task.getDispatchTaskId(), task.getCronJson(), e);
                }
            } else if (DispatchTaskStatus.EXPIRED.getValue().equals(task.getStatus())) {
                // 如果当前是expired状态，但是没有配置cron_json,则保持ac状态
                task.setStatus(DispatchTaskStatus.ACTIVE.getValue());
                task.setUpdateTime(currentTime);
                tasksToUpdate.add(task);
            }
        }

        // 批量更新需要修改状态的任务
        if (!tasksToUpdate.isEmpty()) {
            try {
                for (DispatchTask taskToUpdate : tasksToUpdate) {
                    this.updateById(taskToUpdate);
                }
                log.info("成功更新{}个任务的状态", tasksToUpdate.size());
            } catch (Exception e) {
                log.error("更新任务状态失败", e);
            }
        }
    }

    @Override
    public AppResponse<TerminalTaskDetailVo> getTerminalTaskDetail(String terminalId) {
        try {
            // 构建终端任务详情
            TerminalTaskDetailVo terminalTaskDetail = buildTerminalTaskDetail(terminalId);
            return AppResponse.success(terminalTaskDetail);
        } catch (Exception e) {
            log.error("获取终端任务详情失败，terminalId: {}", terminalId, e);
            // 返回null表示获取失败，具体错误信息已在日志中记录
            return AppResponse.success(null);
        }
    }

    /**
     * 构建终端任务详情
     *
     * @param terminalId 终端ID
     * @return 终端任务详情
     */
    private TerminalTaskDetailVo buildTerminalTaskDetail(String terminalId) {
        TerminalTaskDetailVo terminalTaskDetail =
                TerminalTaskDetailVo.builder().terminalId(terminalId).build();

        // 1. 查询数据库中的正常任务
        terminalTaskDetail.getDispatchTaskInfos().addAll(dispatchTaskDao.selectTaskInfoByTerminalId(terminalId));

        // 2. 重置Redis状态
        RedisUtils.set(RedisKeyUtils.getDispatchTaskStatusKey(terminalId), "0");

        // 3. 从Redis获取并处理特殊任务（手动、重试、停止）
        processRedisTasks(terminalId, terminalTaskDetail);

        // 4. 为所有任务批量填充机器人信息
        populateRobotInfoForAllTasks(terminalTaskDetail);

        return terminalTaskDetail;
    }

    /**
     * 为所有任务填充机器人信息
     */
    private void populateRobotInfoForAllTasks(TerminalTaskDetailVo terminalTaskDetail) {
        // 收集所有任务ID
        List<String> allTaskIds = getAllTaskIds(terminalTaskDetail);

        if (allTaskIds.isEmpty()) {
            return;
        }

        // 批量查询机器人信息并构建映射
        Map<String, List<TerminalTaskDetailVo.DispatchRobotInfo>> taskRobotInfoMap = buildTaskRobotInfoMap(allTaskIds);

        // 为所有任务列表设置机器人信息
        setRobotInfoForAllTaskLists(terminalTaskDetail, taskRobotInfoMap);
    }

    /**
     * 收集所有任务ID
     */
    private List<String> getAllTaskIds(TerminalTaskDetailVo terminalTaskDetail) {
        List<String> allTaskIds = new ArrayList<>();

        // 使用Stream API简化收集逻辑，添加null安全检查
        Stream.of(
                        terminalTaskDetail.getDispatchTaskInfos(),
                        terminalTaskDetail.getRetryTaskInfos(),
                        terminalTaskDetail.getStopTaskInfos())
                .filter(Objects::nonNull)
                .flatMap(List::stream)
                .filter(Objects::nonNull) // 额外保护，防止taskInfo为null
                .map(TerminalTaskDetailVo.DispatchTaskInfo::getTaskId)
                .filter(Objects::nonNull) // 额外保护，防止taskId为null
                .forEach(allTaskIds::add);

        return allTaskIds;
    }

    /**
     * 构建任务ID到机器人信息的映射
     */
    private Map<String, List<TerminalTaskDetailVo.DispatchRobotInfo>> buildTaskRobotInfoMap(List<String> taskIds) {
        List<TerminalTaskDetailVo.DispatchRobotInfo> allRobotInfos = dispatchTaskDao.selectRobotInfoByTaskIds(taskIds);

        return allRobotInfos.stream()
                .filter(robotInfo -> robotInfo.getTaskId() != null)
                .collect(Collectors.groupingBy(TerminalTaskDetailVo.DispatchRobotInfo::getTaskId, Collectors.toList()));
    }

    /**
     * 为所有任务列表设置机器人信息
     */
    private void setRobotInfoForAllTaskLists(
            TerminalTaskDetailVo terminalTaskDetail,
            Map<String, List<TerminalTaskDetailVo.DispatchRobotInfo>> taskRobotInfoMap) {
        Stream.of(
                        terminalTaskDetail.getDispatchTaskInfos(),
                        terminalTaskDetail.getRetryTaskInfos(),
                        terminalTaskDetail.getStopTaskInfos())
                .filter(Objects::nonNull) // 确保List不为null
                .forEach(taskList -> setRobotInfoForTaskList(taskList, taskRobotInfoMap));
    }

    /**
     * 为任务列表设置机器人信息
     */
    private void setRobotInfoForTaskList(
            List<TerminalTaskDetailVo.DispatchTaskInfo> taskList,
            Map<String, List<TerminalTaskDetailVo.DispatchRobotInfo>> taskRobotInfoMap) {
        if (taskList == null || taskList.isEmpty()) {
            return;
        }

        taskList.forEach(taskInfo -> {
            // 安全初始化机器人信息列表
            if (taskInfo.getDispatchRobotInfos() == null) {
                taskInfo.setDispatchRobotInfos(new ArrayList<>());
            }

            List<TerminalTaskDetailVo.DispatchRobotInfo> robotInfos =
                    taskRobotInfoMap.getOrDefault(taskInfo.getTaskId(), new ArrayList<>());
            taskInfo.setDispatchRobotInfos(robotInfos);
        });
    }

    /**
     * 处理Redis中的任务
     */
    private void processRedisTasks(String terminalId, TerminalTaskDetailVo terminalTaskDetail) {
        try {
            String redisListKey = RedisKeyUtils.getDispatchTaskListKey(terminalId);
            long listSize = RedisUtils.lGetListSize(redisListKey);

            if (listSize == 0) {
                log.debug("终端{}的Redis手动任务队列为空", terminalId);
                return;
            }

            // 批量获取Redis任务
            List<Object> redisTasks = getRedisTasks(redisListKey, listSize);
            if (redisTasks.isEmpty()) {
                log.warn("终端{}的Redis手动任务队列弹出失败", terminalId);
                return;
            }

            log.info("从Redis弹出终端{}的{}个手动任务", terminalId, redisTasks.size());

            // 处理任务并设置到对应的列表中
            processAndSetRedisTasks(redisTasks, terminalTaskDetail);

        } catch (Exception e) {
            log.error("从Redis获取手动任务失败: terminalId={}", terminalId, e);
        }
    }

    /**
     * 从Redis获取任务列表
     */
    private List<Object> getRedisTasks(String redisListKey, long listSize) {
        List<Object> redisTasks = new ArrayList<>();

        for (int i = 0; i < listSize; i++) {
            Object task = RedisUtils.redisTemplate.opsForList().leftPop(redisListKey);
            if (task != null) {
                redisTasks.add(task);
            }
        }

        return redisTasks;
    }

    /**
     * 处理并设置Redis任务到对应的任务列表中
     */
    private void processAndSetRedisTasks(List<Object> redisTasks, TerminalTaskDetailVo terminalTaskDetail) {
        // 按任务类型分组
        Map<DispatchTaskFromType, List<String>> taskTypeMap = redisTasks.stream()
                .filter(Objects::nonNull)
                .map(this::extractTaskInfo)
                .filter(Objects::nonNull)
                .collect(Collectors.groupingBy(
                        taskInfo -> taskInfo.getDispatchTaskFromType(),
                        Collectors.mapping(taskInfo -> taskInfo.getDispatchTaskId(), Collectors.toList())));

        // 批量查询并设置任务信息
        taskTypeMap.forEach((taskType, taskIds) -> {
            if (!taskIds.isEmpty()) {
                List<TerminalTaskDetailVo.DispatchTaskInfo> taskInfos = new ArrayList<>();
                taskIds.forEach(taskId -> {
                    TerminalTaskDetailVo.DispatchTaskInfo taskInfo = dispatchTaskDao.selectTaskInfoByTaskId(taskId);
                    if (taskInfo != null) {
                        taskInfos.add(taskInfo);
                    }
                });

                switch (taskType) {
                    case NORMAL:
                        terminalTaskDetail.getDispatchTaskInfos().addAll(taskInfos);
                        break;
                    case RETRY:
                        terminalTaskDetail.getRetryTaskInfos().addAll(taskInfos);
                        break;
                    case STOP:
                        terminalTaskDetail.getStopTaskInfos().addAll(taskInfos);
                        break;
                    default:
                        log.warn("未知的任务类型: {}", taskType);
                        break;
                }
                log.debug("处理了{}个{}任务", taskInfos.size(), taskType.name().toLowerCase());
            }
        });
    }

    /**
     * 从Redis任务对象中提取任务信息
     */
    private RedisListBo extractTaskInfo(Object redisTaskObj) {
        try {
            return (RedisListBo) redisTaskObj;
        } catch (Exception e) {
            log.error("处理Redis中的任务信息失败: redisTaskObj={}", redisTaskObj, e);
            return null;
        }
    }

    /**
     * 轮询检查指定终端是否有任务更新
     *
     * @param terminalId 终端ID
     * @return true表示有数据更新，false表示无数据更新
     */
    public boolean checkTaskUpdate(String terminalId) {
        if (terminalId == null || terminalId.trim().isEmpty()) {
            log.warn("终端ID为空，无法检查任务更新");
            return false;
        }

        try {
            // 检查手动任务队列是否有数据
            String manualTaskKey = RedisKeyUtils.getDispatchTaskListKey(terminalId);
            long manualTaskSize = RedisUtils.lGetListSize(manualTaskKey);
            if (manualTaskSize > 0) {
                log.info("终端{}有手动任务更新，队列大小: {}", terminalId, manualTaskSize);
                return true;
            }

            // 检查其他任务是否有数据
            String scriptTaskKey = RedisKeyUtils.getDispatchTaskStatusKey(terminalId);
            Object scriptTaskValue = RedisUtils.get(scriptTaskKey);
            if (scriptTaskValue != null && "1".equals(scriptTaskValue.toString())) {
                log.info("终端{}有脚本任务更新", terminalId);
                return true;
            }

            log.debug("终端{}无任务更新", terminalId);
            return false;

        } catch (Exception e) {
            log.error("检查终端{}任务更新时发生异常: {}", terminalId, e.getMessage(), e);
            return false;
        }
    }
}
