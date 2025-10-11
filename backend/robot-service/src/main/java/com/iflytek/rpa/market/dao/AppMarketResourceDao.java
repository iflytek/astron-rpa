package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.market.entity.dto.ShareRobotDto;
import com.iflytek.rpa.robot.entity.RobotExecute;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 团队市场-资源映射表(AppMarketResource)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
@Mapper
public interface AppMarketResourceDao extends BaseMapper<AppMarketResource> {

    Integer updateDownloadNum(MarketResourceDto marketResourceDto);

    Integer addAppResource(@Param("entity") ShareRobotDto marketResourceDto);

    Integer updateAppResource(@Param("entity") ShareRobotDto marketResourceDto);

    List<AppMarketResource> getAppInfoByRobotId(@Param("robotId") String robotId, @Param("authorId") String authorId);

    Integer updateAppName(RobotExecute robotExecute);

    Integer selectAppInfo(RobotExecute robotExecute);

    String getAppNameByAppId(@Param("appId") String appId);

    AppMarketResource getAppInfoByAppId(MarketDto marketDto);

    Integer deleteApp(
            @Param("appId") String appId, @Param("marketId") String marketId, @Param("tenantId") String tenantId);

    @Select("select * " + "from app_market_resource "
            + "where app_id = #{appId} and market_id = #{marketId} and deleted = 0")
    AppMarketResource getAppResource(@Param("appId") String appId, @Param("marketId") String marketId);

    @Select("select * " + "from app_market_resource " + "where app_id = #{appId} and market_id = #{marketId}")
    AppMarketResource getAppResourceRegardlessDel(@Param("appId") String appId, @Param("marketId") String marketId);

    @Update("update app_market_resource set download_num=#{downloadNum} where deleted=0 and id=#{resourceId}")
    void syncDownloadNumsWithRedis(@Param("downloadNum") Long downloadNum, @Param("resourceId") Long resourceId);

    @Update("update app_market_resource set check_num=#{checkNum} where deleted=0 and id=#{resourceId}")
    void syncCheckNumsWithRedis(@Param("checkNum") Long checkNum, @Param("resourceId") Long resourceId);
}
