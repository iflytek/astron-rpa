package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.monitor.entity.DeptUser;
import com.iflytek.rpa.monitor.entity.dto.BaseDto;
import com.iflytek.rpa.monitor.entity.dto.HisBaseDto;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.vo.RobotExecuteByNameNDeptVo;
import com.iflytek.rpa.utils.PrePage;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.casbin.casdoor.entity.User;

/**
 * 云端机器人表(RobotExecute)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-22 16:07:33
 */
@Mapper
public interface RobotExecuteDao extends BaseMapper<RobotExecute> {

    List<User> getUnDeployedUserList(
            @Param("entity") QueryUnDeployedUserDto queryUnDeployedUserDto,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    Integer updateResourceStatusByMarketId(
            @Param("resourceStatus") String resourceStatus,
            @Param("userId") String userId,
            @Param("marketId") String marketId);

    Integer countObtainedExecute(MarketResourceDto marketResourceDto);

    Integer countByName(RobotVersionDto robotVersionDto);

    Integer insertRobot(RobotExecute robotExecute);

    Integer updateRobot(RobotExecute robotExecute);

    Integer getObtainCount(MarketResourceDto marketResourceDto);

    Integer updateObtainedRobot(RobotExecute robotExecute);

    Integer insertObtainedRobot(RobotExecute robotExecute);

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

    @Select("select * " + "from robot_execute " + "where robot_id = #{robotId} and deleted = 0")
    RobotExecute getRobotExecuteByRobotId(@Param("robotId") String robotId);

    PrePage<RobotExecute> getDeployedUserList(
            PrePage<RobotExecute> pageConfig,
            @Param("entity") MarketDto marketDto,
            @Param("databaseName") String databaseName);

    PrePage<DeployedUserDto> getCloudDeployedUserList(
            PrePage<DeployedUserDto> pageConfig,
            @Param("entity") QueryDeployedUserDto queryDeployedUserDto,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    RobotExecute getAuthInfo(AppMarketResource appMarketResource);

    DeployedUserDto getAuthInfoForDeployed(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    Integer deleteExecute(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

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

    List<HisBaseDto> countRobotTotalNumByDate(
            @Param("endOfDay") String endOfDay, @Param("deptUserList") List<DeptUser> deptUserList);

    List<RobotExecuteByNameNDeptVo> getRobotExecuteByNameNDept(RobotExecuteByNameNDeptDto queryDto);

    List<RobotExecute> getRobotExecuteByName(
            @Param("name") String name, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<RobotNameDto> getRobotNameListByName(@Param("name") String robotName, @Param("entity") BaseDto baseDto);

    /**
     * 调度模块-查询租户内所有可用机器人列表（包含版本信息）
     *
     * @param name     机器人名称（可为空）
     * @param tenantId 租户ID
     * @return 机器人列表
     */
    List<RobotExecute> getRobotListForDispatch(@Param("name") String name, @Param("tenantId") String tenantId);

    List<RobotExecute> getRobotListForRule(@Param("name") String name, @Param("tenantId") String tenantId);
}
