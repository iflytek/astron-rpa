package com.iflytek.rpa.dispatch.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.dispatch.entity.DispatchTask;
import com.iflytek.rpa.dispatch.entity.DispatchTaskExecuteRecord;
import com.iflytek.rpa.dispatch.entity.DispatchTaskRobotExecuteRecord;
import com.iflytek.rpa.dispatch.entity.dto.RobotExecuteStatusDto;
import com.iflytek.rpa.dispatch.entity.dto.TaskExecuteStatusDto;
import com.iflytek.rpa.robot.entity.vo.RecordLogVo;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface DispatchTaskExecuteRecordDao extends BaseMapper<DispatchTaskExecuteRecord> {

    Integer getMaxBatch(Long dispatchTaskId);

    void insertTaskExecuteRecord(DispatchTaskExecuteRecord taskExecuteRecord);

    Integer updateTaskExecuteStatus(@Param("entity") TaskExecuteStatusDto statusDto);

    DispatchTask selectTaskById(Long dispatchTaskId);

    DispatchTaskExecuteRecord selectByExecuteId(Long taskExecuteId);

    void insertRobotExecuteRecord(RobotExecuteStatusDto recordDto);

    DispatchTaskRobotExecuteRecord getRobotExecuteRecord(RobotExecuteStatusDto recordDto);

    Integer updateRobotExecuteRecord(RobotExecuteStatusDto recordDto);

    RecordLogVo getRobotExecuteLog(@Param("executeId") Long executeId, @Param("tenantId") String tenantId);
}
