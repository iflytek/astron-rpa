package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.ResourceConfigDto;
import java.util.Map;

/**
 * 租户资源服务接口
 */
public interface TenantResourceService {

    /**
     * 获取租户的资源配置（带缓存）
     * @param tenantId 租户ID
     * @return 资源配置Map，key为resourceCode，value为ResourceConfigDto（已补充完整信息）
     */
    Map<String, ResourceConfigDto> getTenantResourceConfig(String tenantId);

    /**
     * 重新生成并更新租户的配置JSON
     * 当租户修改配额时调用此方法，直接修改final值
     * @param tenantId 租户ID
     * @param quotaUpdates 配额更新记录，key为resourceCode，value为新的final值
     */
    void regenerateTenantConfig(String tenantId, Map<String, Integer> quotaUpdates);

    /**
     * 清除租户配置缓存
     * @param tenantId 租户ID
     */
    void clearTenantConfigCache(String tenantId);

    /**
     * 根据资源代码获取资源配置
     * @param tenantId 租户ID
     * @param resourceCode 资源代码
     * @return 资源配置，如果不存在返回null
     */
    ResourceConfigDto getResourceConfig(String tenantId, String resourceCode);
}
