package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.monitor.entity.RobotMonitorDto;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import java.util.Date;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 云端机器人执行记录表(RobotExecute)表数据库访问层
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Mapper
public interface RobotExecuteRecordDao extends BaseMapper<RobotExecuteRecord> {

    IPage<RobotExecuteRecord> getExecuteRecordList(
            IPage<RobotExecuteRecord> pageConfig, @Param("entity") ExecuteRecordDto recordDto);

    List<RobotExecuteRecord> getRecordByExecuteIdList(@Param("executeIdList") List<String> executeIdList);

    RobotMonitorDto robotOverview(
            @Param("tenantId") String tenantId,
            @Param("robotId") String robotId,
            @Param("countTime") Date countTime,
            @Param("robotVersion") Integer robotVersion);

    String getExecuteLog(ExecuteRecordDto recordDto);

    RobotExecuteRecord getExecuteRecord(ExecuteRecordDto recordDto);

    Integer insertExecuteRecord(ExecuteRecordDto recordDto);

    Integer updateExecuteRecord(ExecuteRecordDto recordDto);

    @Update("update robot_execute_record " + "set deleted = 1 "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0")
    Integer deleteRecord(
            @Param("tenantId") String tenantId, @Param("robotId") String robotId, @Param("userId") String userId);

    @Select("select id " + "from robot_execute_record "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0")
    List<Integer> getRecordIds(
            @Param("tenantId") String tenantId, @Param("robotId") String robotId, @Param("userId") String userId);

    @Update("<script>" + "update robot_execute_record "
            + "set deleted = 1 "
            + "where id in "
            + "<foreach collection='idList' item='id' open='(' separator=',' close=')'>"
            + "#{id}"
            + "</foreach>"
            + "</script>")
    Integer deleteRecordByIds(@Param("idList") List<Integer> idList);

    Integer batchDeleteByTaskExecuteIds(
            @Param("taskExecuteIdList") List<String> taskExecuteIdList,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    int deleteRobotExecuteRecords(List<String> recordsIds, String userId, String tenantId);
}
