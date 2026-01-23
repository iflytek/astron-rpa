package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.market.entity.AppMarket;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 团队市场-团队表(AppMarket)表数据库访问层
 *
 * @author makejava
 * @since 2024-01-19 14:41:29
 */
@Mapper
public interface AppMarketDao extends BaseMapper<AppMarket> {

    List<AppMarket> getJoinedMarketList(@Param("userId") String userId);

    List<AppMarket> getCreatedMarketList(@Param("tenantId") String tenantId, @Param("userId") String userId);

    List<AppMarket> getMarketList(@Param("tenantId") String tenantId, @Param("userId") String userId);

    List<AppMarket> getTenantMarketList(@Param("tenantId") String tenantId);

    Integer addMarket(@Param("entity") AppMarket appMarket);

    Integer getMarketNameByName(@Param("tenantId") String tenantId, @Param("marketName") String marketName);

    Integer updateTeamMarket(AppMarket appMarket);

    AppMarket getMarketInfo(@Param("marketId") String marketId);

    Integer deleteMarket(@Param("marketId") String marketId);

    String getCreator(@Param("marketId") String marketId);

    Integer updateTeamMarketOwner(@Param("marketId") String marketId, @Param("newOwnerId") String newOwnerId);

    String getMarketNameById(@Param("marketId") String marketId);

    Integer getMarketCount(String tenantId);

    AppMarket selectPublicMarket(String tenantId);

    Integer addMarketWithType(@Param("entity") AppMarket appMarket);
}
