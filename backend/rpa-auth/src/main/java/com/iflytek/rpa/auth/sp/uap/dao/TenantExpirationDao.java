package com.iflytek.rpa.auth.sp.uap.dao;

import com.iflytek.rpa.auth.sp.uap.entity.TenantExpiration;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 租户到期信息数据访问接口
 *
 * @author system
 */
@Mapper
public interface TenantExpirationDao {

    /**
     * 根据租户ID查询租户到期信息
     *
     * @param tenantId 租户ID
     * @return 租户到期信息
     */
    TenantExpiration queryByTenantId(@Param("tenantId") String tenantId);
}
