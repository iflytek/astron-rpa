package com.iflytek.rpa.astronAgent.dao;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * AstronAgent数据访问层
 */
@Mapper
public interface AstronAgentDao {

    /**
     * 根据用户ID获取租户ID列表
     * @param databaseName 数据库名
     * @param userId 用户ID
     * @return 租户ID列表
     */
    List<String> getTenantIdsByUserId(@Param("databaseName") String databaseName, @Param("userId") String userId);

    /**
     * 根据租户ID列表获取个人租户ID
     * @param databaseName 数据库名
     * @param tenantIds 租户ID列表
     * @return 个人租户ID
     */
    String getPersonalTenantId(@Param("databaseName") String databaseName, @Param("tenantIds") List<String> tenantIds);
}
