package com.iflytek.rpa.robot.service;

import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.utils.response.AppResponse;

public interface RobotIconService {
    AppResponse<?> RobotIconModeHandler(RobotIconDto dto) throws Exception;
}
