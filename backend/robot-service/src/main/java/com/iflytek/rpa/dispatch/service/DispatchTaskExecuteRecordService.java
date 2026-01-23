package com.iflytek.rpa.dispatch.service;

import com.iflytek.rpa.dispatch.entity.dto.RobotExecuteStatusDto;
import com.iflytek.rpa.dispatch.entity.dto.TaskExecuteStatusDto;
import com.iflytek.rpa.robot.entity.vo.RecordLogVo;
import com.iflytek.rpa.utils.exception.NoLoginException;
import com.iflytek.rpa.utils.response.AppResponse;

public interface DispatchTaskExecuteRecordService {
    AppResponse<String> reportTaskStatus(TaskExecuteStatusDto statusDto) throws NoLoginException;

    AppResponse<String> reportRobotStatus(RobotExecuteStatusDto statusDto) throws NoLoginException;

    AppResponse<RecordLogVo> getRobotExecuteLog(Long executeId) throws NoLoginException;
}
