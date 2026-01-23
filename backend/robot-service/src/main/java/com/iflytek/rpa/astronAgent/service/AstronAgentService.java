package com.iflytek.rpa.astronAgent.service;

import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotDto;
import com.iflytek.rpa.astronAgent.entity.dto.CopyRobotResponseDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdDto;
import com.iflytek.rpa.astronAgent.entity.dto.GetUserIdResponseDto;
import com.iflytek.rpa.utils.response.AppResponse;

/**
 * AstronAgent服务接口
 */
public interface AstronAgentService {

    /**
     * 复制机器人到目标用户的个人租户下
     * @param copyRobotDto 复制机器人请求参数
     * @return 复制后的机器人id
     */
    AppResponse<CopyRobotResponseDto> copyRobot(CopyRobotDto copyRobotDto);

    /**
     * 通过手机号获取用户ID
     * @param getUserIdDto 获取用户ID请求参数
     * @return 用户ID
     */
    AppResponse<GetUserIdResponseDto> getUserIdByPhone(GetUserIdDto getUserIdDto);
}
