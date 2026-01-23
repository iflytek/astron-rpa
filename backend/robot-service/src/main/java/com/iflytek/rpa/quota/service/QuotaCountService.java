package com.iflytek.rpa.quota.service;

/**
 * 配额数量查询服务接口
 * 提供各种资源的当前数量查询（带缓存）
 */
public interface QuotaCountService {

    /**
     * 获取设计器数量（当前租户下用户创建的机器人数量）
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @return 设计器数量
     */
    Integer getDesignerCount(String tenantId, String userId);

    /**
     * 获取市场加入数量（用户已加入的市场数量）
     *
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @return 已加入的市场数量
     */
    Integer getMarketJoinCount(String tenantId, String userId);
}
