package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.AppMarketVersion;
import com.iflytek.rpa.market.entity.dto.MarketResourceDto;
import com.iflytek.rpa.market.entity.dto.ResVerDto;
import com.iflytek.rpa.market.entity.dto.ShareRobotDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 团队市场-应用版本表(AppMarketVersion)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-23 17:12:48
 */
@Mapper
public interface AppMarketVersionDao extends BaseMapper<AppMarketVersion> {

    Integer insertAppVersionBatch(
            @Param("latestAppVersionInfo") AppMarketVersion latestAppVersion,
            @Param("appInfoList") List<AppMarketResource> appInfoList);

    Integer addAppVersionBatch(@Param("entity") ShareRobotDto marketResourceDto);

    Integer updateAppVersionBatch(@Param("entity") ShareRobotDto marketResourceDto);

    Integer deleteAppVersion(@Param("appId") String appId, @Param("marketId") String marketId);

    AppMarketVersion getLatestAppVersionInfo(MarketResourceDto marketResourceDto);

    @Select("select * " + "from app_market_version "
            + "where app_id = #{appId} and market_id = #{marketId} and deleted = 0 "
            + "order by app_version desc")
    List<AppMarketVersion> getAllAppVersion(@Param("appId") String appId, @Param("marketId") String marketId);

    @Select("select * " + "from app_market_version "
            + "where app_id = #{appId} and market_id = #{marketId} "
            + "order by app_version desc")
    List<AppMarketVersion> getAllAppVersionRegardlessDel(
            @Param("appId") String appId, @Param("marketId") String marketId);

    @Select("select * " + "from app_market_version "
            + "where app_id = #{appId} and market_id = #{marketId} and deleted = 0 "
            + "order by app_version desc limit 1")
    AppMarketVersion getLatestAppVersion(@Param("appId") String appId, @Param("marketId") String marketId);

    List<AppMarketVersion> getAppVersionList(
            @Param("marketId") String marketId, @Param("appIdList") List<String> appIdList);

    List<ResVerDto> getResVerJoin(@Param("marketId") String marketId, @Param("appIdList") List<String> appIdList);
}
