package com.iflytek.rpa.market.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.market.entity.AppMarket;
import com.iflytek.rpa.market.entity.AppMarketUser;
import com.iflytek.rpa.market.entity.MarketDto;
import com.iflytek.rpa.market.entity.TenantUser;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 团队市场-人员表，n:n的关系(AppMarketUser)表数据库访问层
 *
 * @author makejava
 * @since 2024-01-19 14:41:35
 */
@Mapper
public interface AppMarketUserDao extends BaseMapper<AppMarketUser> {

    List<AppMarketUser> getUserListForUpdate(@Param("marketId") String marketId, @Param("appId") String appId);

    Integer addDefaultUser(@Param("entity") AppMarketUser appMarketUser);

    IPage<MarketDto> getUserList(
            IPage<MarketDto> pageConfig,
            @Param("entity") MarketDto marketDto,
            @Param("databaseName") String databaseName);

    Integer deleteUser(@Param("entity") MarketDto marketDto);

    Integer roleSet(@Param("entity") MarketDto marketDto);

    String getOwnerByRole(@Param("marketId") String marketId);

    String getUserTypeForCheck(@Param("userId") String userId, @Param("marketId") String marketId);

    List<MarketDto> getUserUnDeployed(@Param("entity") MarketDto marketDto, @Param("databaseName") String databaseName);

    List<MarketDto> getUserByPhone(@Param("entity") MarketDto marketDto, @Param("databaseName") String databaseName);

    List<MarketDto> getUserByPhoneForOwner(
            @Param("entity") MarketDto marketDto, @Param("databaseName") String databaseName);

    @Select("select creator_id " + "from app_market_user "
            + "where deleted = 0 and market_id = #{marketId} and tenant_id = #{tenantId}")
    List<Long> getAllUserId(@Param("tenantId") String tenantId, @Param("marketId") String marketId);

    List<TenantUser> getTenantUser(
            @Param("tenantId") String tenantId,
            @Param("entities") List<AppMarketUser> userInfoList,
            @Param("databaseName") String databaseName);

    Integer leaveTeamMarket(@Param("entity") AppMarket appMarket);

    Integer updateToOwner(@Param("marketId") String marketId, @Param("newOwnerId") String newOwnerId);

    Integer deleteAllUser(@Param("marketId") String marketId);

    Set<String> getMarketUserListForDeploy(
            @Param("marketId") String marketId, @Param("userIdList") List<String> userIdList);

    /**
     * 统计总行数
     *
     * @param appMarketUser 查询条件
     * @return 总行数
     */
    long count(AppMarketUser appMarketUser);

    @Select(
            "select user_type from app_market_user where deleted=0 and market_id=#{marketId} and creator_id=#{creatorId}")
    String getUserType(@Param("marketId") String marketId, @Param("creatorId") String creatorId);

    @Select(
            "select count(id) from app_market_user where deleted=0 and market_id=#{marketId} and creator_id=#{creatorId} and tenant_id=#{tenantId}")
    Integer isInMarket(
            @Param("marketId") String marketId,
            @Param("creatorId") String creatorId,
            @Param("tenantId") String tenantId);

    @Select("select * from app_market_user where deleted=0 and market_id=#{marketId} and creator_id=#{creatorId}")
    AppMarketUser getMarketUser(@Param("marketId") String marketId, @Param("creatorId") String creatorId);

    @Select("select user_type " + "from app_market_user "
            + "where deleted=0 and market_id=#{marketId} and creator_id=#{userId} and tenant_id = #{tenantId}")
    String getMarketUserType(
            @Param("marketId") String marketId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<String> getMarketUserInList(
            @Param("marketId") String marketId,
            @Param("userIdList") List<String> userIdList,
            @Param("tenantId") String tenantId);
}
