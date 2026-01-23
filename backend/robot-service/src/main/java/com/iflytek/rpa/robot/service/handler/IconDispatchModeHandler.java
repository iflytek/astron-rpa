package com.iflytek.rpa.robot.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.DISPATCH;

import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.robot.entity.vo.RobotIconVo;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class IconDispatchModeHandler implements RobotIconModeHandler {
    @Autowired
    RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Override
    public boolean supports(String mode) {
        return DISPATCH.equals(mode);
    }

    @Override
    public AppResponse<RobotIconVo> handle(RobotIconDto dto) throws Exception {
        RobotExecute executeInfo = getRobotExecute(dto.getRobotId());
        Integer enabledVersion = dto.getRobotVersion();
        return handleDataSource(executeInfo, enabledVersion);
    }

    private AppResponse<RobotIconVo> handleDataSource(RobotExecute executeInfo, Integer enabledVersion) {
        // 指定版本
        executeInfo.setAppVersion(enabledVersion);
        executeInfo.setRobotVersion(enabledVersion);
        if ("create".equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, enabledVersion);
        } else if ("market".equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, enabledVersion);
        } else if ("deploy".equals(executeInfo.getDataSource())) {
            return handleDeploySource(executeInfo, enabledVersion);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    private AppResponse<RobotIconVo> handleDeploySource(RobotExecute robotExecute, Integer robotVersion) {
        RobotIconVo vo = robotVersionDao.getDeployInfo(robotExecute);
        return AppResponse.success(vo);
    }

    private AppResponse<RobotIconVo> handleMarketSource(RobotExecute robotExecute, Integer robotVersion) {
        RobotIconVo vo = robotVersionDao.getMarketInfo(robotExecute);
        return AppResponse.success(vo);
    }

    private AppResponse<RobotIconVo> handleCreateSource(RobotExecute robotExecute, Integer robotVersion) {
        String robotId = robotExecute.getRobotId();
        RobotVersion version = robotVersionDao.getVersion(robotId, robotVersion);
        String icon = version.getIcon();
        String name = robotExecute.getName();
        return AppResponse.success(new RobotIconVo(name, icon));
    }

    private RobotExecute getRobotExecute(String robotId) {
        return robotExecuteDao.getRobotExecuteByRobotId(robotId);
    }
}
