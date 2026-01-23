package com.iflytek.rpa.robot.service.handler;

import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.robot.entity.vo.RobotIconVo;
import com.iflytek.rpa.utils.response.AppResponse;

public interface RobotIconModeHandler {
    boolean supports(String mode);

    AppResponse<RobotIconVo> handle(RobotIconDto dto) throws Exception;
}
