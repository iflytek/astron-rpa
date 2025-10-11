package com.iflytek.rpa.monitor.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.monitor.entity.HisRobot;
import com.iflytek.rpa.robot.entity.vo.RobotExecutionData;
import com.iflytek.rpa.robot.entity.vo.RobotExecutionTrendData;
import java.util.Date;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 单个机器人趋势表(HisCloudRobot)表数据库访问层
 *
 * @author mjren
 * @since 2023-04-12 16:45:08
 */
@Mapper
public interface HisRobotDao extends BaseMapper<HisRobot> {

    Integer insertBatch(@Param("entities") List<HisRobot> hisRobotBatchData);

    List<RobotExecutionTrendData> getExecuteDataHistory(String robotId, Date startTime, Date endTime);

    RobotExecutionData getRobotHistoryExecutionData(String robotId, Date endTime);
}
