package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.robot.entity.File;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.robot.entity.vo.RobotIconVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 云端机器人版本表(RobotVersion)表数据库访问层
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Mapper
public interface RobotVersionDao extends BaseMapper<RobotVersion> {
    Integer getOnlineVersionByRobotId(@Param("robotId") String robotId);

    RobotVersion getVersionInfo(MarketResourceDto marketResourceDto);

    List<RobotVersion> getVersionListForApp(MarketDto marketDto);

    Integer addRobotVersion(RobotVersion robotVersion);

    RobotVersionDto getLatestRobotVersion(@Param("appId") String appId);

    RobotVersion getLastRobotVersionInfo(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<File> getFileNameInfo(@Param("fileIdList") List<String> fileIdList);

    Integer getLatestVersionNum(RobotVersionDto robotVersionDto);

    Integer unEnableAllVersion(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and online = 1")
    RobotVersion getOriEnableVersion(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Update(
            "update robot_version " + "set online = 1 "
                    + "where robot_id = #{robotId} and version = #{version} and creator_id = #{userId} and tenant_id = #{tenantId}")
    boolean enableVersion(
            @Param("robotId") String robotId,
            @Param("version") Integer version,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} "
            + "order by version desc")
    List<RobotVersion> getAllVersion(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and tenant_id = #{tenantId} "
            + "order by version desc")
    List<RobotVersion> getAllVersionWithoutUserId(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId}  and tenant_id = #{tenantId} "
            + "order by version desc")
    List<RobotVersion> getDeployAllVersion(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0 "
            + "order by version desc "
            + "limit 1")
    RobotVersion getLatestVersion(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select(
            "select * " + "from robot_version "
                    + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0 and online = 1")
    RobotVersion getEnableVersion(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and tenant_id = #{tenantId} and deleted = 0 and online = 1")
    RobotVersion getDeployEnableVersion(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId}  "
            + "order by version desc "
            + "limit 1")
    RobotVersion getLatestVersionRegardlessDel(@Param("robotId") String robotId);

    @Select("select * " + "from robot_version " + "where robot_id = #{robotId} and online = 1 ")
    RobotVersion getOnlineVersionRegardlessDel(@Param("robotId") String robotId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and version = #{versionNum} and deleted = 0")
    RobotVersion getVersion(@Param("robotId") String robotId, @Param("versionNum") Integer versionNum);

    @Select("select file_name from file where file_id = #{fileId} and deleted = 0")
    String getFileName(@Param("fileId") String fileId);

    @Select("select * " + "from robot_version "
            + "where robot_id = #{robotId} and deleted = 0 "
            + "order by version desc")
    List<RobotVersion> getAllVersionWithoutUser(@Param("robotId") String robotId);

    RobotIconVo getMarketInfo(RobotExecute executeInfo);

    RobotIconVo getDeployInfo(RobotExecute executeInfo);

    Integer getRobotVersion(String robotId);
}
