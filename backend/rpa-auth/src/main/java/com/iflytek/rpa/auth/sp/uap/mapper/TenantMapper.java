package com.iflytek.rpa.auth.sp.uap.mapper;

import com.iflytek.rpa.auth.core.entity.Tenant;
import com.iflytek.rpa.auth.sp.uap.constants.UAPConstant;
import com.iflytek.sec.uap.client.core.dto.tenant.UapTenant;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;

/**
 * Tenant映射器
 * 用于将UAP客户端的UapTenant转换为core包下的Tenant
 *
 * @author xqcao2
 */
@Component
public class TenantMapper {

    /**
     * 将UAP客户端的UapTenant转换为核心实体Tenant
     *
     * @param uapTenant UAP客户端的UapTenant
     * @return core包下的Tenant
     */
    public Tenant fromUapTenant(UapTenant uapTenant) {
        if (uapTenant == null) {
            return null;
        }

        Tenant tenant = new Tenant();
        // 使用BeanUtils复制属性
        BeanUtils.copyProperties(uapTenant, tenant);

        if (uapTenant.getTenantCode() == null
                || uapTenant.getTenantCode().startsWith(UAPConstant.PERSONAL_TENANT_CODE)) {
            tenant.setTenantType(UAPConstant.TENANT_TYPE_PERSONAL);
        } else if (uapTenant.getTenantCode().startsWith(UAPConstant.PROFESSIONAL_TENANT_CODE)) {
            tenant.setTenantType(UAPConstant.TENANT_TYPE_PROFESSIONAL);
        } else if (uapTenant.getTenantCode().startsWith(UAPConstant.ENTERPRISE_PURCHASED_TENANT_CODE)) {
            tenant.setTenantType(UAPConstant.TENANT_TYPE_ENTERPRISE_PURCHASED);
        } else if (uapTenant.getTenantCode().startsWith(UAPConstant.ENTERPRISE_SUBSCRIPTION_TENANT_CODE)) {
            tenant.setTenantType(UAPConstant.TENANT_TYPE_ENTERPRISE_SUBSCRIPTION);
        }

        return tenant;
    }
}
