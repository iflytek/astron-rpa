package com.iflytek.rpa.monitor.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.monitor.entity.HisDataEnum;
import com.iflytek.rpa.monitor.entity.HisRobot;
import com.iflytek.rpa.monitor.entity.dto.BaseDto;
import com.iflytek.rpa.monitor.entity.dto.RobotRecordDto;
import com.iflytek.rpa.monitor.entity.vo.RobotStatisticsVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletResponse;

public interface HisRobotService extends IService<HisRobot> {

    AppResponse<List<HisDataEnum>> robotExecuteToday(BaseDto baseDto) throws NoLoginException;

    AppResponse<IPage<RobotStatisticsVo>> getRobotExecuteList(RobotRecordDto queryDto) throws NoLoginException;

    void getRobotExecuteExcel(RobotRecordDto queryDto, HttpServletResponse response);

    void insertBatch(List<HisRobot> hisRobotBatchData);
}
