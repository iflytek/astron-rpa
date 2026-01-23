package com.iflytek.rpa.robot.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.EXECUTOR;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.robot.entity.vo.RobotIconVo;
import com.iflytek.rpa.utils.StringUtils;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class IconExecutorModeHandler implements RobotIconModeHandler {
    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public boolean supports(String mode) {
        return EXECUTOR.equals(mode);
    }

    @Override
    public AppResponse<RobotIconVo> handle(RobotIconDto dto) throws Exception {
        RobotExecute robotExecute = getRobotExecute(dto.getRobotId());
        return handleDataSource(robotExecute, dto.getRobotVersion());
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

    private AppResponse<RobotIconVo> handleDataSource(RobotExecute robotExecute, Integer robotVersion)
            throws JsonProcessingException {
        if (robotVersion != null) {
            robotExecute.setAppVersion(robotVersion);
            robotExecute.setRobotVersion(robotVersion);
        }
        if ("market".equals(robotExecute.getDataSource())) {
            return handleMarketSource(robotExecute, robotVersion);
        } else if ("create".equals(robotExecute.getDataSource())) {
            return handleCreateSource(robotExecute);
        } else if ("deploy".equals(robotExecute.getDataSource())) {
            return handleDeploySource(robotExecute, robotVersion);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    private AppResponse<RobotIconVo> handleMarketSource(RobotExecute executeInfo, Integer robotVersion) {
        RobotIconVo vo = robotVersionDao.getMarketInfo(executeInfo);
        return AppResponse.success(vo);
    }

    private AppResponse<RobotIconVo> handleCreateSource(RobotExecute robotExecute) {
        String robotId = robotExecute.getRobotId();
        // 获取启用中的 版本
        Integer enabledVersion = robotVersionDao.getRobotVersion(robotId);

        RobotVersion version = robotVersionDao.getVersion(robotId, enabledVersion);
        String icon = version.getIcon();
        if (StringUtils.isEmpty(icon)) {
            icon = "";
        }
        String name = robotExecute.getName();
        return AppResponse.success(new RobotIconVo(name, icon));
    }

    private AppResponse<RobotIconVo> handleDeploySource(RobotExecute robotExecute, Integer robotVersion) {
        RobotIconVo vo = robotVersionDao.getDeployInfo(robotExecute);
        return AppResponse.success(vo);
    }
}
