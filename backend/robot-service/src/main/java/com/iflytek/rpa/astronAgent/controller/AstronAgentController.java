package com.iflytek.rpa.astronAgent.controller;

import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotDto;
import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotResponseDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdResponseDto;
import com.iflytek.rpa.astronAgent.service.AstronAgentService;
import com.iflytek.rpa.utils.response.AppResponse;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

/**
 * AstronAgent控制器
 */
@RestController
@RequestMapping("/astron-agent")
public class AstronAgentController {

    @Resource
    private AstronAgentService astronAgentService;

    /**
     * 复制机器人到目标用户的个人租户下
     * @param copyRobotDto 复制机器人请求参数
     * @return 复制后的机器人id
     */
    @PostMapping("/copy-robot")
    public AppResponse<CopyRobotResponseDto> copyRobot(@Valid @RequestBody CopyRobotDto copyRobotDto) {
        return astronAgentService.copyRobot(copyRobotDto);
    }

    /**
     * 通过手机号获取用户ID
     * @param getUserIdDto 获取用户ID请求参数
     * @return 用户ID
     */
    @PostMapping("/get-user-id")
    public AppResponse<GetUserIdResponseDto> getUserIdByPhone(@Valid @RequestBody GetUserIdDto getUserIdDto) {
        return astronAgentService.getUserIdByPhone(getUserIdDto);
    }
}
