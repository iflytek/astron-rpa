package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.SysTenantConfig;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 租户配置表 Mapper 接口
 */
@Mapper
public interface SysTenantConfigDao extends BaseMapper<SysTenantConfig> {

    /**
     * 根据租户ID查询租户配置
     */
    @Select("SELECT * FROM sys_tenant_config WHERE tenant_id = #{tenantId} AND deleted = 0 LIMIT 1")
    SysTenantConfig selectByTenantId(@Param("tenantId") String tenantId);
}
