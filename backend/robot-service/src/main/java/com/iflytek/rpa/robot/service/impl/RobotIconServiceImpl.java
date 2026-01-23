package com.iflytek.rpa.robot.service.impl;

import com.iflytek.rpa.robot.entity.dto.RobotIconDto;
import com.iflytek.rpa.robot.service.RobotIconService;
import com.iflytek.rpa.robot.service.handler.RobotIconHandlerFactory;
import com.iflytek.rpa.robot.service.handler.RobotIconModeHandler;
import com.iflytek.rpa.utils.response.AppResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service("robotIconService")
public class RobotIconServiceImpl implements RobotIconService {

    private final RobotIconHandlerFactory robotIconHandlerFactory;

    public RobotIconServiceImpl(RobotIconHandlerFactory robotIconHandlerFactory) {
        this.robotIconHandlerFactory = robotIconHandlerFactory;
    }

    @Override
    public AppResponse<?> RobotIconModeHandler(RobotIconDto dto) throws Exception {

        String mode = dto.getMode();
        RobotIconModeHandler handler = robotIconHandlerFactory.getHandler(mode);
        return handler.handle(dto);
    }
}
