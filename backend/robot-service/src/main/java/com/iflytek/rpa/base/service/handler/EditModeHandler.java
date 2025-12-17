package com.iflytek.rpa.base.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;
import static com.iflytek.rpa.robot.constants.RobotConstant.PROJECT_LIST;

import com.iflytek.rpa.base.dao.CParamDao;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.*;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-04-17 14:59
 * @copyright Copyright (c) 2025 mjren
 */
@Component
@RequiredArgsConstructor
public class EditModeHandler implements ParamModeHandler {
    private static final Set<String> SUPPORT_MODES = new HashSet<>(Arrays.asList(EDIT_PAGE, PROJECT_LIST));

    private final CParamDao cParamDao;

    @Override
    public boolean supports(String mode) {
        return SUPPORT_MODES.contains(mode);
    }

    @Override
    public AppResponse<List<ParamDto>> handle(QueryParamDto dto) {
        Integer robotVersion = 0;
        if (dto.getRobotVersion() != null) {
            robotVersion = dto.getRobotVersion();
        }
        // python模块获取配置参数
        String moduleId = dto.getModuleId();
        if (StringUtils.isNotBlank(moduleId)) {
            return moduleHandle(dto, moduleId, robotVersion);
        }
        // 主/子流程获取配置参数
        String processId = dto.getProcessId();
        return processHandle(dto, processId, robotVersion);
    }

    private AppResponse<List<ParamDto>> moduleHandle(QueryParamDto dto, String moduleId, Integer robotVersion) {
        List<CParam> params = cParamDao.getParamsByModuleId(moduleId, dto.getRobotId(), robotVersion);
        return AppResponse.success(convertParams(params));
    }

    @NotNull
    private AppResponse<List<ParamDto>> processHandle(QueryParamDto dto, String processId, Integer robotVersion) {
        if (StringUtils.isBlank(dto.getProcessId())) {
            // 默认查主流程参数
            processId = cParamDao.getMianProcessId(dto.getRobotId(), robotVersion);
        }
        List<CParam> params = cParamDao.getAllParams(processId, dto.getRobotId(), robotVersion);
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
}
