package com.iflytek.rpa.robot.service;

import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.EnableVersionDto;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.robot.entity.dto.VersionListDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 云端机器人版本表(RobotVersion)表服务接口
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
public interface RobotVersionService {

    AppResponse<?> publishRobot(RobotVersionDto robotVersionDto) throws Exception;

    AppResponse<?> checkSameName(RobotVersionDto robotVersionDto) throws NoLoginException;

    AppResponse<?> getLastRobotVersionInfo(RobotVersion robotVersion) throws NoLoginException;

    AppResponse<?> versionList(VersionListDto queryDto) throws NoLoginException;

    AppResponse<?> enableVersion(EnableVersionDto queryDto) throws Exception;

    AppResponse<?> recoverVersion(EnableVersionDto queryDto) throws Exception;

    AppResponse<?> list4Design(String robotId) throws NoLoginException;

    void updateAppAndRobot(RobotExecute robotExecute, Integer nextVersion) throws NoLoginException;
}
