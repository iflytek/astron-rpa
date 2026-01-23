package com.iflytek.rpa.auth.sp.uap.dao;

import com.iflytek.rpa.auth.core.entity.UserEntitlement;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 用户权益数据访问接口
 *
 * @author system
 */
@Mapper
public interface UserEntitlementDao {

    /**
     * 根据用户ID和租户ID查询用户权益
     *
     * @param userId   用户ID
     * @param tenantId 租户ID
     * @return 用户权益信息
     */
    UserEntitlement queryByUserIdAndTenantId(@Param("userId") String userId, @Param("tenantId") String tenantId);
}
