package com.iflytek.rpa.quota.service.impl;

import com.iflytek.rpa.base.entity.dto.ResourceConfigDto;
import com.iflytek.rpa.base.service.TenantResourceService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.User;
import com.iflytek.rpa.quota.service.QuotaCheckService;
import com.iflytek.rpa.quota.service.QuotaCountService;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * 配额校验工具类
 * 提供统一的配额校验方法，包含缓存机制
 */
@Slf4j
@Component
public class QuotaCheckServiceImpl implements QuotaCheckService {

    @Autowired
    private TenantResourceService tenantResourceService;

    @Autowired
    private QuotaCountService quotaCountService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public boolean checkDesignerQuota() {
        return checkQuota("designer_count", () -> {
            String tenantId = getTenantId();
            String userId = getUserId();
            return quotaCountService.getDesignerCount(tenantId, userId);
        });
    }

    @Override
    public boolean checkMarketJoinQuota() {
        return checkQuota("market_join_count", () -> {
            String tenantId = getTenantId();
            String userId = getUserId();
            return quotaCountService.getMarketJoinCount(tenantId, userId);
        });
    }

    /**
     * 校验配额并抛出异常（如果超限）
     * @param resourceCode 资源代码
     * @param currentCountSupplier 获取当前数量的函数
     * @throws ServiceException 如果配额超限
     */
    private boolean checkQuota(String resourceCode, java.util.function.Supplier<Integer> currentCountSupplier) {
        try {
            // 获取租户ID
            String tenantId = getTenantId();
            if (StringUtils.isBlank(tenantId)) {
                log.warn("无法获取租户ID，跳过配额校验");
                return true;
            }

            // 获取资源配置
            ResourceConfigDto config = tenantResourceService.getResourceConfig(tenantId, resourceCode);
            if (config == null) {
                log.warn("资源配置不存在，跳过配额校验，resourceCode: {}", resourceCode);
                return true;
            }

            // 检查父级资源是否有效
            if (StringUtils.isNotBlank(config.getParent())) {
                ResourceConfigDto parentConfig = tenantResourceService.getResourceConfig(tenantId, config.getParent());
                if (parentConfig == null || parentConfig.getFinalValue() == null || parentConfig.getFinalValue() == 0) {
                    throw new ServiceException("父级资源未启用");
                }
            }

            // 获取配额限制
            Integer quotaLimit = config.getFinalValue();
            if (quotaLimit == null || quotaLimit < 0) {
                // -1表示不限，直接通过
                return true;
            }

            // 获取当前数量（使用缓存）
            Integer currentCount = currentCountSupplier.get();
            if (currentCount == null) {
                currentCount = 0;
            }

            // 校验配额
            if (currentCount >= quotaLimit) {
                log.warn(
                        "配额已超限，resourceCode: {}, currentCount: {}, quotaLimit: {}",
                        resourceCode,
                        currentCount,
                        quotaLimit);
                return false;
            }

            return true;
        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("配额校验失败，resourceCode: {}", resourceCode, e);
            // 发生异常时，为了不影响业务，返回true（允许通过）
            return true;
        }
    }

    /**
     * 获取租户ID
     */
    private String getTenantId() {
        try {
            AppResponse<String> response = rpaAuthFeign.getTenantId();
            if (response != null && response.ok() && response.getData() != null) {
                return response.getData();
            }
        } catch (Exception e) {
            log.debug("从认证服务获取租户ID失败", e);
        }
        return null;
    }

    /**
     * 获取用户ID
     */
    private String getUserId() {
        try {
            AppResponse<User> response = rpaAuthFeign.getLoginUser();
            if (response != null && response.ok() && response.getData() != null) {
                return response.getData().getId();
            }
        } catch (Exception e) {
            log.debug("从认证服务获取用户ID失败", e);
        }
        return null;
    }
}
