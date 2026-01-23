package com.iflytek.rpa.auth.dataPreheater.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.auth.dataPreheater.entity.AppMarketUser;
import java.util.List;
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

    Integer addDefaultUser(@Param("entity") AppMarketUser appMarketUser);

    Integer addUser(@Param("entity") AppMarketUser appMarketUser);

    @Select("select creator_id " + "from app_market_user "
            + "where deleted = 0 and market_id = #{marketId} and tenant_id = #{tenantId}")
    List<String> getAllUserId(@Param("tenantId") String tenantId, @Param("marketId") String marketId);

    /**
     * 统计总行数
     *
     * @param appMarketUser 查询条件
     * @return 总行数
     */
    long count(AppMarketUser appMarketUser);

    void insertBatch(List<AppMarketUser> insertBatchList);
}
