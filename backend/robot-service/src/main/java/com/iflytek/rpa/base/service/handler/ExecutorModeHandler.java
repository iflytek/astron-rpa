package com.iflytek.rpa.base.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.EXECUTOR;

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
 * @date 2025-04-17 15:01
 * @copyright Copyright (c) 2025 mjren
 */
@Component
@RequiredArgsConstructor
public class ExecutorModeHandler implements ParamModeHandler {
    private final CParamDao cParamDao;
    private final RobotExecuteDao robotExecuteDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public boolean supports(String mode) {
        return EXECUTOR.equals(mode);
    }

    @Override
    public AppResponse<List<ParamDto>> handle(QueryParamDto dto) throws JsonProcessingException, NoLoginException {
        RobotExecute executeInfo = getRobotExecute(dto.getRobotId());

        return handleDataSource(executeInfo, dto.getProcessId(), dto.getModuleId(), dto.getRobotVersion());
    }

    /**
     * 内部调用获取参数
     *
     * @param dto
     * @return
     * @throws JsonProcessingException
     * @throws NoLoginException
     */
    public AppResponse<List<ParamDto>> getParamInside(QueryParamDto dto, String userId, String tenantId)
            throws JsonProcessingException {
        RobotExecute executeInfo = getRobotExecuteInside(dto.getRobotId(), userId, tenantId);

        return handleDataSource(executeInfo, dto.getProcessId(), dto.getModuleId(), dto.getRobotVersion());
    }

    private RobotExecute getRobotExecuteInside(String robotId, String userId, String tenantId) {
        RobotExecute executeInfo = robotExecuteDao.getRobotInfoByRobotId(robotId, userId, tenantId);
        if (executeInfo == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "无法获取执行器机器人信息");
        }
        return executeInfo;
    }

    private RobotExecute getRobotExecute(String robotId) throws NoLoginException {
        AppResponse<User> response = rpaAuthFeign.getLoginUser();
        if (response == null || !response.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        User loginUser = response.getData();
        String userId = loginUser.getId();
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();

        RobotExecute executeInfo = robotExecuteDao.getRobotInfoByRobotId(robotId, userId, tenantId);
        if (executeInfo == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "无法获取执行器机器人信息");
        }
        return executeInfo;
    }

    private AppResponse<List<ParamDto>> handleDataSource(
            RobotExecute executeInfo, String processId, String moduleId, Integer robotVersion)
            throws JsonProcessingException {
        if (robotVersion != null) {
            executeInfo.setAppVersion(robotVersion);
            executeInfo.setRobotVersion(robotVersion);
        }
        if ("create".equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, processId, moduleId);
        } else if ("market".equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, processId, moduleId);
        } else if ("deploy".equals(executeInfo.getDataSource())) {
            return handleDeploySource(executeInfo, processId, moduleId);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    private AppResponse<List<ParamDto>> handleDeploySource(RobotExecute executeInfo, String processId, String moduleId)
            throws JsonProcessingException {
        String originRobotId = cParamDao.getDeployOriginalRobotId(executeInfo);

        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return deployModuleHandle(executeInfo, moduleId, originRobotId);
        }

        return deployProcessHandle(executeInfo, processId, originRobotId);
    }

    private AppResponse<List<ParamDto>> deployModuleHandle(
            RobotExecute executeInfo, String moduleId, String originRobotId) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> deployProcessHandle(
            RobotExecute executeInfo, String processId, String originRobotId) throws JsonProcessingException {
        if (executeInfo.getParamDetail() != null) {
            return parseCustomParams(executeInfo.getParamDetail());
        }
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleMarketSource(RobotExecute executeInfo, String processId, String moduleId)
            throws JsonProcessingException {
        validateMarketInfo(executeInfo);
        String originRobotId = cParamDao.getMarketRobotId(executeInfo);
        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return marketModuleHandle(executeInfo, moduleId, originRobotId);
        }
        // 流程
        return marketProcessHandle(executeInfo, processId, originRobotId);
    }

    private AppResponse<List<ParamDto>> marketModuleHandle(
            RobotExecute executeInfo, String moduleId, String originRobotId) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> marketProcessHandle(
            RobotExecute executeInfo, String processId, String originRobotId) throws JsonProcessingException {
        if (executeInfo.getParamDetail() != null) {
            return parseCustomParams(executeInfo.getParamDetail());
        }
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleCreateSource(RobotExecute executeInfo, String processId, String moduleId)
            throws JsonProcessingException {
        Integer enabledVersion = cParamDao.getRobotVersion(executeInfo.getRobotId());
        if (executeInfo.getRobotVersion() != null) {
            enabledVersion = executeInfo.getRobotVersion();
        }
        // python模块
        if (!StringUtils.isEmpty(moduleId)) {
            return createModuleHandle(executeInfo, moduleId, enabledVersion);
        }
        // 流程
        return createProcessHandle(executeInfo, processId, enabledVersion);
    }

    private AppResponse<List<ParamDto>> createModuleHandle(
            RobotExecute executeInfo, String moduleId, Integer enabledVersion) {
        List<CParam> params = cParamDao.getSelfRobotParamByModuleId(executeInfo.getRobotId(), moduleId, enabledVersion);
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> createProcessHandle(
            RobotExecute executeInfo, String processId, Integer enabledVersion) throws JsonProcessingException {
        String mainProcessId = cParamDao.getMianProcessId(executeInfo.getRobotId(), enabledVersion);
        // processId == null 不能改 执行器配置参数获取有用
        if (processId == null || mainProcessId.equals(processId)) {
            if (executeInfo.getParamDetail() != null) {
                return parseCustomParams(executeInfo.getParamDetail());
            } else {
                processId = mainProcessId;
            }
        }
        List<CParam> params = cParamDao.getSelfRobotParam(executeInfo.getRobotId(), processId, enabledVersion);
        return AppResponse.success(convertParams(params));
    }

    private void validateMarketInfo(RobotExecute executeInfo) {
        if (StringUtils.isAnyBlank(executeInfo.getMarketId(), executeInfo.getAppId())
                || executeInfo.getAppVersion() == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "机器人市场信息异常");
        }
    }

    private AppResponse<List<ParamDto>> parseCustomParams(String paramDetail) throws JsonProcessingException {
        List<CParam> params = objectMapper.readValue(paramDetail, new TypeReference<List<CParam>>() {});
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

    /**
     * 内部调用获取参数
     * @param dto
     * @return
     * @throws JsonProcessingException
     * @throws NoLoginException
     */
    public AppResponse<List<ParamDto>> getParamInside4NewVersion(
            QueryParamDto dto, String userId, String tenantId, Integer version) throws JsonProcessingException {
        RobotExecute executeInfo = getRobotExecuteInside(dto.getRobotId(), userId, tenantId);
        dto.setRobotVersion(version);
        String processId = robotExecuteDao.getProcessId(executeInfo.getRobotId());

        return handleDataSource(executeInfo, processId, dto.getModuleId(), dto.getRobotVersion());
    }
}
