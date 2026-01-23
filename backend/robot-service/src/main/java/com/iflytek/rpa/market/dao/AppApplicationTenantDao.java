package com.iflytek.rpa.market.dao;

import com.iflytek.rpa.market.entity.AppApplicationTenant;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface AppApplicationTenantDao {
    
    /**
     * 根据租户ID查询审核开关状态
     * @param tenantId 租户ID
     * @return 审核开关状态
     */
    AppApplicationTenant getByTenantId(@Param("tenantId") String tenantId);
    
    /**
     * 更新审核开关状态
     * @param tenantId 租户ID
     * @param auditEnable 审核开关状态 1-启用 0-禁用
     * @param operator 操作人
     * @param reason 变更原因
     * @return 更新结果
     */
    int updateAuditEnable(@Param("tenantId") String tenantId, @Param("auditEnable") Short auditEnable,
                         @Param("operator") String operator, @Param("reason") String reason);
    
    /**
     * 插入审核开关配置
     * @param tenantId 租户ID
     * @param auditEnable 审核开关状态 1-启用 0-禁用
     * @param operator 操作人
     * @param reason 变更原因
     * @return 插入结果
     */
    int insertOrUpdateAuditEnable(@Param("tenantId") String tenantId, @Param("auditEnable") Short auditEnable,
                                 @Param("operator") String operator, @Param("reason") String reason);
    

}
