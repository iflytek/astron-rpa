package com.iflytek.rpa.base.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.CRONTAB;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.dao.CParamDao;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.task.service.ScheduleTaskRobotService;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-04-17 15:02
 * @copyright Copyright (c) 2025 mjren
 */
@Component
@RequiredArgsConstructor
public class TriggerModeHandler implements ParamModeHandler {
    private final ScheduleTaskRobotService scheduleTaskRobotService;
    private final RobotExecuteDao robotExecuteDao;
    private final CParamDao cParamDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public boolean supports(String mode) {
        return CRONTAB.equals(mode);
    }

    @Override
    public AppResponse<List<ParamDto>> handle(QueryParamDto dto) throws JsonProcessingException, NoLoginException {
        ScheduleTaskRobot taskRobot = getTaskRobot(dto.getTaskRobotUniqueId());

        if (null != taskRobot && StringUtils.isNotBlank(taskRobot.getParamJson())) {
            return parseCustomParams(taskRobot.getParamJson());
        }

        RobotExecute executeInfo = getRobotExecute(dto.getRobotId());
        if (dto.getRobotVersion() != null) {
            executeInfo.setRobotVersion(dto.getRobotVersion());
            executeInfo.setAppVersion(dto.getRobotVersion());
        }
        return handleDataSource(executeInfo, dto.getProcessId(), dto.getModuleId());
    }

    private ScheduleTaskRobot getTaskRobot(Long uniqueId) {
        if (uniqueId == null) {
            return null;
        }
        ScheduleTaskRobot taskRobot = scheduleTaskRobotService.queryById(uniqueId);
        if (taskRobot == null) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "未找到对应的计划任务机器人");
        }
        return taskRobot;
    }

    private RobotExecute getRobotExecute(String robotId) throws NoLoginException {
        AppResponse<User> resp = rpaAuthFeign.getLoginUser();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = resp.getData();
        String userId = loginUser.getId();

        AppResponse<String> res = rpaAuthFeign.getTenantId();
        if (res == null || res.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = res.getData();

        RobotExecute executeInfo = robotExecuteDao.getRobotInfoByRobotId(robotId, userId, tenantId);
        if (executeInfo == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "无法获取执行器机器人信息");
        }
        return executeInfo;
    }

    private AppResponse<List<ParamDto>> handleDataSource(RobotExecute executeInfo, String processId, String moduleId) {
        if ("market".equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, processId, moduleId);
        } else if ("create".equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, processId, moduleId);
        }
        throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "未知数据来源类型");
    }

    // 以下复用ExecutorModeHandler中的handleMarketSource/handleCreateSource逻辑
    // 实际项目中应考虑抽取公共组件
    private AppResponse<List<ParamDto>> handleMarketSource(
            RobotExecute executeInfo, String processId, String moduleId) {
        validateMarketInfo(executeInfo);
        String originRobotId = cParamDao.getMarketRobotId(executeInfo);

        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return marketModuleHandle(executeInfo, moduleId, originRobotId);
        }
        return marketProcessHandle(executeInfo, processId, originRobotId);
    }

    private AppResponse<List<ParamDto>> marketModuleHandle(
            RobotExecute executeInfo, String moduleId, String originRobotId) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> marketProcessHandle(
            RobotExecute executeInfo, String processId, String originRobotId) {
        String mainProcessId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        List<CParam> params = cParamDao.getAllParams(
                processId != null ? processId : mainProcessId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleCreateSource(
            RobotExecute executeInfo, String processId, String moduleId) {
        Integer enabledVersion = cParamDao.getRobotVersion(executeInfo.getRobotId());
        if (executeInfo.getRobotVersion() != null) {
            enabledVersion = executeInfo.getRobotVersion();
        }
        String mainProcessId = cParamDao.getMianProcessId(executeInfo.getRobotId(), enabledVersion);
        List<CParam> params = cParamDao.getSelfRobotParam(
                executeInfo.getRobotId(),
                StringUtils.isNotBlank(processId) ? processId : mainProcessId,
                enabledVersion);
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> createModuleHandle(
            RobotExecute executeInfo, String moduleId, Integer enabledVersion) {
        List<CParam> params = cParamDao.getSelfRobotParamByModuleId(executeInfo.getRobotId(), moduleId, enabledVersion);
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> parseCustomParams(String paramJson) throws JsonProcessingException {
        List<CParam> params = objectMapper.readValue(paramJson, new TypeReference<List<CParam>>() {});
        return AppResponse.success(convertParams(params));
    }

    private List<ParamDto> convertParams(List<CParam> params) {
        if (CollectionUtils.isEmpty(params)) {
            return Collections.emptyList();
        }
        return params.stream()
                .map(p -> {
                    ParamDto dto = new ParamDto();
                    BeanUtils.copyProperties(p, dto);
                    return dto;
                })
                .collect(Collectors.toList());
    }

    private void validateMarketInfo(RobotExecute executeInfo) {
        if (StringUtils.isAnyBlank(executeInfo.getMarketId(), executeInfo.getAppId())
                || executeInfo.getAppVersion() == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "机器人市场信息异常");
        }
    }
}
