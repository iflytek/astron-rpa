package com.iflytek.rpa.robot.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;
import static com.iflytek.rpa.robot.constants.RobotConstant.PROJECT_LIST;

import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.robot.entity.vo.RobotIconVo;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class IconEditModeHandler implements RobotIconModeHandler {
    private static final Set<String> SUPPORT_MODES = new HashSet<>(Arrays.asList(EDIT_PAGE, PROJECT_LIST));

    @Autowired
    RobotDesignDao robotDesignDao;

    @Autowired
    RobotVersionDao robotVersionDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public boolean supports(String mode) {
        return SUPPORT_MODES.contains(mode);
    }

    @Override
    public AppResponse<RobotIconVo> handle(RobotIconDto dto) throws Exception {
        Integer robotVersion = 0;
        if (dto.getRobotVersion() != null) {
            robotVersion = dto.getRobotVersion();
        }
        String robotId = dto.getRobotId();
        RobotVersion version = robotVersionDao.getVersion(robotId, robotVersion);
        String icon = "", name = "";
        if (version != null) {
            icon = version.getIcon();
        }
        AppResponse<String> resp = rpaAuthFeign.getTenantId();
        if (resp == null || resp.getData() == null) {
            throw new ServiceException("租户信息获取失败");
        }
        String tenantId = resp.getData();
        RobotDesign robot = robotDesignDao.getRobotInfoAll(robotId, tenantId);
        if (robot != null) {
            name = robot.getName();
        }
        //        RobotVersion version = robotVersionDao.getVersion(robotId, robotVersion);
        //        if(version == null){
        //            return AppResponse.success(new RobotIconVo(name, ""));
        //        }
        //        String icon = version.getIcon();
        return AppResponse.success(new RobotIconVo(name, icon));
    }
}
