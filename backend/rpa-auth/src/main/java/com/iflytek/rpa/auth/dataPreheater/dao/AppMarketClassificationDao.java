package com.iflytek.rpa.auth.dataPreheater.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.auth.dataPreheater.entity.AppMarketClassification;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 应用市场分类表(AppMarketClassification)数据库访问层
 *
 * @author auto-generated
 */
@Mapper
public interface AppMarketClassificationDao extends BaseMapper<AppMarketClassification> {

    Integer insertDefaultClassification(@Param("tenantId") String tenantId);

    /**
     * 根据租户ID查询分类数据行数
     *
     * @param tenantId 租户ID
     * @return 数据行数
     */
    Integer countByTenantId(@Param("tenantId") String tenantId);
}
