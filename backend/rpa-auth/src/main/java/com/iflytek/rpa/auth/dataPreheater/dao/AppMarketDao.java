package com.iflytek.rpa.auth.dataPreheater.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.auth.dataPreheater.entity.AppMarket;
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
    AppMarket selectPublicMarket(String tenantId);

    Integer addMarketWithType(@Param("entity") AppMarket appMarket);
}
