package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.market.entity.vo.AppMarketUserVo;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.dto.DeployedUserDto;
import com.iflytek.rpa.robot.entity.dto.QueryDeployedUserDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteByNameNDeptDto;
import com.iflytek.rpa.robot.entity.vo.RobotExecuteByNameNDeptVo;
import com.iflytek.rpa.utils.PrePage;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 云端机器人表(RobotExecute)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-22 16:07:33
 */
@Mapper
public interface RobotExecuteDao extends BaseMapper<RobotExecute> {

    Integer updateResourceStatusByMarketId(
            @Param("resourceStatus") String resourceStatus,
            @Param("userId") String userId,
            @Param("marketId") String marketId);

    List<AppMarketUserVo> getObtainerIdList(
            @Param("marketIdList") List<String> marketIdList,
            @Param("appIdList") List<String> appIdList,
            @Param("authorId") String authorId);

    Integer countObtainedExecute(MarketResourceDto marketResourceDto);

    Integer insertRobot(RobotExecute robotExecute);

    Integer updateRobot(RobotExecute robotExecute);

    Integer getObtainCount(MarketResourceDto marketResourceDto);

    Integer updateObtainedRobot(RobotExecute robotExecute);

    Integer insertObtainedRobot(RobotExecute robotExecute);

    Integer updateResourceStatusByAppIdList(
            @Param("resourceStatus") String resourceStatus,
            @Param("appIdList") List<String> appIdList,
            @Param("marketUserList") List<AppMarketUserVo> marketUserList);

    RobotExecute queryByRobotId(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    Integer updateParamToNUll(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    Integer updateRobotByPull(RobotExecute robotExecute);

    Integer addRobotByDeploy(@Param("entities") List<RobotExecute> robotExecuteList);

    Set<String> getUserListByAppId(@Param("appId") String appId);

    Integer updateRobotByPush(@Param("entity") MarketDto marketDto);

    RobotExecute getRobotInfoByRobotId(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    Integer saveParamInfo(RobotExecute robotExecute);

    @Select("select * " + "from robot_execute "
            + "where deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and robot_id = #{robotId}")
    RobotExecute getRobotExecute(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_execute " + "where tenant_id = #{tenantId} and robot_id = #{robotId}")
    RobotExecute getRobotExecuteByTenantId(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_execute "
            + "where robot_id = #{robotId} and deleted = 0 and resource_status is null")
    RobotExecute getRobotExecuteByRobotId(@Param("robotId") String robotId);

    PrePage<DeployedUserDto> getCloudDeployedUserList(
            PrePage<DeployedUserDto> pageConfig,
            @Param("entity") QueryDeployedUserDto queryDeployedUserDto,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    RobotExecute getAuthInfo(AppMarketResource appMarketResource);

    Integer deleteExecute(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select id " + "from robot_execute "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0")
    Integer getExecuteId(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Update("update robot_execute " + "set deleted = 1 " + "where id = #{id}")
    Integer deleteExecuteById(@Param("id") Integer id);

    @Select("select file_name from file where file_id = #{fileId} and deleted = 0")
    String getFileName(@Param("fileId") String fileId);

    List<RobotExecute> getExecuteByAppIdList(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("marketId") String marketId,
            @Param("appIdList") List<String> appIdList);

    @Select("select * " + "from robot_execute "
            + "where deleted = 0 and creator_id = #{userId} and market_id = #{marketId} and tenant_id = #{tenantId} and app_id = #{appId} "
            + "order by app_version desc "
            + "limit 1")
    RobotExecute getExecuteByAppId(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("marketId") String marketId,
            @Param("appId") String appId);

    List<RobotExecute> getExeByAppIdsRobotIds(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("queryInfoList") List<RobotExecute> queryInfoList);

    List<RobotExecuteByNameNDeptVo> getRobotExecuteByNameNDept(RobotExecuteByNameNDeptDto queryDto);

    List<RobotExecute> getRobotExecuteByName(
            @Param("name") String name, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select robot_id from robot_execute where deleted = 0 and creator_id = #{userId} and name = #{name}")
    String getExpoUserRobotId(@Param("name") String name, @Param("userId") String userId);

    @Select("select process_id from c_process where robot_id = #{robotId} and robot_version = 1")
    String getProcessId(@Param("robotId") String robotId);
}
