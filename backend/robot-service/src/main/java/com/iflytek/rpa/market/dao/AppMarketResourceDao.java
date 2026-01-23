package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.market.entity.AppMarketResource;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.dto.ShareRobotDto;
import com.iflytek.rpa.robot.entity.RobotExecute;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 团队市场-资源映射表(AppMarketResource)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-21 14:36:30
 */
@Mapper
public interface AppMarketResourceDao extends BaseMapper<AppMarketResource> {

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

    /**
     * 分页查询市场应用资源
     */
    Page<AppMarketResource> pageAllAppList(
            IPage<AppMarketResource> pageConfig,
            @Param("marketId") String marketId,
            @Param("creatorId") String creatorId,
            @Param("appName") String appName,
            @Param("category") String category,
            @Param("sortKey") String sortKey);
}
