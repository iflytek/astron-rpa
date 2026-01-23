package com.iflytek.rpa.base.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.TypeReference;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.SysProductVersionDao;
import com.iflytek.rpa.base.dao.SysTenantConfigDao;
import com.iflytek.rpa.base.dao.SysVersionDefaultConfigDao;
import com.iflytek.rpa.base.entity.SysProductVersion;
import com.iflytek.rpa.base.entity.SysTenantConfig;
import com.iflytek.rpa.base.entity.SysVersionDefaultConfig;
import com.iflytek.rpa.base.entity.dto.ResourceConfigDto;
import com.iflytek.rpa.base.service.TenantResourceService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.common.feign.entity.TenantExpirationDto;
import com.iflytek.rpa.utils.RedisUtils;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.AppResponse;
import java.util.*;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 租户资源服务实现类
 */
@Slf4j
@Service
public class TenantResourceServiceImpl extends ServiceImpl<SysTenantConfigDao, SysTenantConfig>
        implements TenantResourceService {

    private static final String REDIS_KEY_PREFIX = "tenant:resource:config:";
    private static final long CACHE_EXPIRE_SECONDS = 3600; // 缓存1小时

    @Autowired
    private SysTenantConfigDao sysTenantConfigDao;

    @Autowired
    private SysVersionDefaultConfigDao sysVersionDefaultConfigDao;

    @Autowired
    private SysProductVersionDao sysProductVersionDao;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    @Override
    public Map<String, ResourceConfigDto> getTenantResourceConfig(String tenantId) {
        if (StringUtils.isBlank(tenantId)) {
            return Collections.emptyMap();
        }

        // 先从Redis缓存获取
        String cacheKey = REDIS_KEY_PREFIX + tenantId;
        Object cached = RedisUtils.get(cacheKey);
        if (cached != null) {
            try {
                String jsonStr = cached.toString();
                return JSON.parseObject(jsonStr, new TypeReference<Map<String, ResourceConfigDto>>() {});
            } catch (Exception e) {
                log.warn("解析缓存配置失败，将从数据库重新加载，tenantId: {}", tenantId, e);
            }
        }

        // 从数据库获取
        SysTenantConfig tenantConfig = sysTenantConfigDao.selectByTenantId(tenantId);
        if (tenantConfig == null) {
            // 如果租户配置不存在，尝试初始化
            return initializeTenantConfig(tenantId);
        }

        // 构建全量配置
        return buildFullConfig(tenantConfig);
    }

    /**
     * 初始化租户配置（从版本默认配置生成）
     * 直接返回全量配置，不需要补全逻辑
     */
    private Map<String, ResourceConfigDto> initializeTenantConfig(String tenantId) {
        try {
            // 获取租户的版本信息
            Long versionId = getTenantVersionId(tenantId);
            if (versionId == null) {
                log.warn("无法获取租户版本信息，tenantId: {}", tenantId);
                return Collections.emptyMap();
            }

            // 获取版本默认配置
            List<SysVersionDefaultConfig> defaultConfigs = sysVersionDefaultConfigDao.selectByVersionId(versionId);
            if (defaultConfigs.isEmpty()) {
                log.warn("版本默认配置为空，versionId: {}", versionId);
                return Collections.emptyMap();
            }

            // 构建全量配置Map
            Map<String, ResourceConfigDto> fullConfigMap = new HashMap<>();
            for (SysVersionDefaultConfig config : defaultConfigs) {
                ResourceConfigDto dto = new ResourceConfigDto();
                dto.setType(config.getResourceType() == 1 ? "QUOTA" : "SWITCH");
                dto.setBase(config.getDefaultValue());
                dto.setFinalValue(config.getDefaultValue());
                dto.setParent(config.getParentCode());

                // 解析URL patterns
                if (StringUtils.isNotBlank(config.getUrlPatterns())) {
                    try {
                        List<String> urls = JSON.parseArray(config.getUrlPatterns(), String.class);
                        dto.setUrls(urls);
                    } catch (Exception e) {
                        log.warn("解析URL patterns失败，resourceCode: {}", config.getResourceCode(), e);
                        dto.setUrls(Collections.emptyList());
                    }
                } else {
                    dto.setUrls(Collections.emptyList());
                }

                fullConfigMap.put(config.getResourceCode(), dto);
            }

            // 保存到数据库（extraConfigJson为空，因为没有修改项）
            SysTenantConfig tenantConfig = new SysTenantConfig();
            tenantConfig.setTenantId(tenantId);
            tenantConfig.setVersionId(versionId);
            tenantConfig.setExtraConfigJson("{}"); // 空JSON对象，表示没有修改项
            tenantConfig.setDeleted(0);
            tenantConfig.setCreateTime(new Date());
            tenantConfig.setUpdateTime(new Date());
            sysTenantConfigDao.insert(tenantConfig);

            // 存入缓存
            String cacheKey = REDIS_KEY_PREFIX + tenantId;
            RedisUtils.set(cacheKey, JSON.toJSONString(fullConfigMap), CACHE_EXPIRE_SECONDS);

            return fullConfigMap;
        } catch (Exception e) {
            log.error("初始化租户配置失败，tenantId: {}", tenantId, e);
            return Collections.emptyMap();
        }
    }

    /**
     * 获取租户的版本ID
     * 这里需要根据实际业务逻辑实现，可能需要从租户信息中获取
     */
    private Long getTenantVersionId(String tenantId) {
        // 这里先查询租户配置表，如果存在则返回其versionId
        SysTenantConfig tenantConfig = sysTenantConfigDao.selectByTenantId(tenantId);
        if (tenantConfig != null && tenantConfig.getVersionId() != null) {
            return tenantConfig.getVersionId();
        }

        // 如果不存在，默认返回个人版（versionCode = "personal"）
        AppResponse<TenantExpirationDto> resp = rpaAuthFeign.getExpiration();
        if (resp == null || !resp.ok()) {
            throw new ServiceException("用户信息获取失败");
        }
        TenantExpirationDto data = resp.getData();
        String tenantType = data.getTenantType();
        SysProductVersion version;
        if (tenantType.equals("professional")) {
            version = sysProductVersionDao.selectByVersionCode("professional");
        } else if (tenantType.startsWith("enterprise_")) {
            // 企业版不限制
            version = null;
        } else {
            version = sysProductVersionDao.selectByVersionCode("personal");
        }
        return version != null ? version.getId() : null;
    }

    /**
     * 构建全量配置
     * 从版本默认配置和修改项构建完整的配置信息
     */
    private Map<String, ResourceConfigDto> buildFullConfig(SysTenantConfig tenantConfig) {
        Long versionId = tenantConfig.getVersionId();

        // 获取版本默认配置
        List<SysVersionDefaultConfig> defaultConfigs = sysVersionDefaultConfigDao.selectByVersionId(versionId);
        if (defaultConfigs.isEmpty()) {
            log.warn("版本默认配置为空，versionId: {}", versionId);
            return Collections.emptyMap();
        }

        // 解析修改项（extraConfigJson），只存储有修改的资源
        // extraConfigJson只包含type、base、final字段，不包含urls和parent
        Map<String, ResourceConfigDto> modifiedConfigMap = new HashMap<>();
        if (StringUtils.isNotBlank(tenantConfig.getExtraConfigJson())
                && !"{}".equals(tenantConfig.getExtraConfigJson())) {
            try {
                // 先解析为Map<String, Map<String, Object>>
                Map<String, Map<String, Object>> rawMap = JSON.parseObject(
                        tenantConfig.getExtraConfigJson(), new TypeReference<Map<String, Map<String, Object>>>() {});
                // 转换为ResourceConfigDto（只包含type、base、final）
                for (Map.Entry<String, Map<String, Object>> entry : rawMap.entrySet()) {
                    Map<String, Object> configMap = entry.getValue();
                    ResourceConfigDto dto = new ResourceConfigDto();
                    dto.setType((String) configMap.get("type"));
                    dto.setBase(((Number) configMap.get("base")).intValue());
                    dto.setFinalValue(((Number) configMap.get("final")).intValue());
                    modifiedConfigMap.put(entry.getKey(), dto);
                }
            } catch (Exception e) {
                log.warn("解析修改配置失败，tenantId: {}", tenantConfig.getTenantId(), e);
            }
        }

        // 构建全量配置Map
        Map<String, ResourceConfigDto> fullConfigMap = new HashMap<>();
        for (SysVersionDefaultConfig defaultConfig : defaultConfigs) {
            ResourceConfigDto dto = new ResourceConfigDto();
            dto.setType(defaultConfig.getResourceType() == 1 ? "QUOTA" : "SWITCH");
            dto.setBase(defaultConfig.getDefaultValue());
            dto.setParent(defaultConfig.getParentCode());

            // 如果有修改项，使用修改后的final值，否则使用默认值
            ResourceConfigDto modifiedConfig = modifiedConfigMap.get(defaultConfig.getResourceCode());
            if (modifiedConfig != null && modifiedConfig.getFinalValue() != null) {
                dto.setFinalValue(modifiedConfig.getFinalValue());
            } else {
                dto.setFinalValue(defaultConfig.getDefaultValue());
            }

            // 解析URL patterns
            if (StringUtils.isNotBlank(defaultConfig.getUrlPatterns())) {
                try {
                    List<String> urls = JSON.parseArray(defaultConfig.getUrlPatterns(), String.class);
                    dto.setUrls(urls);
                } catch (Exception e) {
                    log.warn("解析URL patterns失败，resourceCode: {}", defaultConfig.getResourceCode(), e);
                    dto.setUrls(Collections.emptyList());
                }
            } else {
                dto.setUrls(Collections.emptyList());
            }

            fullConfigMap.put(defaultConfig.getResourceCode(), dto);
        }

        // 存入缓存
        String cacheKey = REDIS_KEY_PREFIX + tenantConfig.getTenantId();
        RedisUtils.set(cacheKey, JSON.toJSONString(fullConfigMap), CACHE_EXPIRE_SECONDS);

        return fullConfigMap;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void regenerateTenantConfig(String tenantId, Map<String, Integer> quotaUpdates) {
        if (StringUtils.isBlank(tenantId) || quotaUpdates == null || quotaUpdates.isEmpty()) {
            return;
        }

        try {
            // 获取租户配置记录
            SysTenantConfig tenantConfig = sysTenantConfigDao.selectByTenantId(tenantId);
            if (tenantConfig == null) {
                log.warn("租户配置记录不存在，tenantId: {}", tenantId);
                return;
            }

            // 获取版本默认配置，用于获取base值
            Long versionId = tenantConfig.getVersionId();
            List<SysVersionDefaultConfig> defaultConfigs = sysVersionDefaultConfigDao.selectByVersionId(versionId);
            Map<String, SysVersionDefaultConfig> defaultConfigMap = defaultConfigs.stream()
                    .collect(Collectors.toMap(SysVersionDefaultConfig::getResourceCode, config -> config));

            // 解析现有的修改项
            Map<String, ResourceConfigDto> currentModifiedMap = new HashMap<>();
            if (StringUtils.isNotBlank(tenantConfig.getExtraConfigJson())
                    && !"{}".equals(tenantConfig.getExtraConfigJson())) {
                try {
                    currentModifiedMap = JSON.parseObject(
                            tenantConfig.getExtraConfigJson(), new TypeReference<Map<String, ResourceConfigDto>>() {});
                } catch (Exception e) {
                    log.warn("解析现有修改配置失败，tenantId: {}", tenantId, e);
                }
            }

            // 更新final值（直接设置，不计算差值）
            for (Map.Entry<String, Integer> entry : quotaUpdates.entrySet()) {
                String resourceCode = entry.getKey();
                Integer newFinalValue = entry.getValue();

                // 获取默认配置以获取base值
                SysVersionDefaultConfig defaultConfig = defaultConfigMap.get(resourceCode);
                if (defaultConfig == null) {
                    log.warn("资源代码不存在于默认配置中，resourceCode: {}", resourceCode);
                    continue;
                }

                ResourceConfigDto modifiedConfig = currentModifiedMap.get(resourceCode);
                if (modifiedConfig == null) {
                    modifiedConfig = new ResourceConfigDto();
                    modifiedConfig.setType(defaultConfig.getResourceType() == 1 ? "QUOTA" : "SWITCH");
                    modifiedConfig.setBase(defaultConfig.getDefaultValue());
                    currentModifiedMap.put(resourceCode, modifiedConfig);
                }

                // 直接设置final值
                modifiedConfig.setFinalValue(newFinalValue);
            }

            // 构建新的修改JSON（只存储有修改的资源，final值等于base的不存储）
            // 注意：只保存type、base、final字段，不保存urls和parent
            Map<String, Map<String, Object>> newModifiedMap = new HashMap<>();
            for (Map.Entry<String, ResourceConfigDto> entry : currentModifiedMap.entrySet()) {
                ResourceConfigDto config = entry.getValue();
                // 只存储final值不等于base的资源
                if (config.getFinalValue() != null
                        && config.getBase() != null
                        && !config.getFinalValue().equals(config.getBase())) {
                    Map<String, Object> configMap = new HashMap<>();
                    configMap.put("type", config.getType());
                    configMap.put("base", config.getBase());
                    configMap.put("final", config.getFinalValue());
                    newModifiedMap.put(entry.getKey(), configMap);
                }
            }

            // 保存到数据库（只保存修改项，如果没有修改项则为空JSON对象）
            if (newModifiedMap.isEmpty()) {
                tenantConfig.setExtraConfigJson("{}");
            } else {
                tenantConfig.setExtraConfigJson(JSON.toJSONString(newModifiedMap));
            }
            tenantConfig.setUpdateTime(new Date());
            sysTenantConfigDao.updateById(tenantConfig);

            // 清除缓存，下次获取时会重新构建
            clearTenantConfigCache(tenantId);

            log.info("租户配置更新成功，tenantId: {}, quotaUpdates: {}", tenantId, quotaUpdates);
        } catch (Exception e) {
            log.error("重新生成租户配置失败，tenantId: {}", tenantId, e);
            throw new RuntimeException("重新生成租户配置失败", e);
        }
    }

    @Override
    public void clearTenantConfigCache(String tenantId) {
        if (StringUtils.isBlank(tenantId)) {
            return;
        }
        String cacheKey = REDIS_KEY_PREFIX + tenantId;
        RedisUtils.del(cacheKey);
    }

    @Override
    public ResourceConfigDto getResourceConfig(String tenantId, String resourceCode) {
        Map<String, ResourceConfigDto> configMap = getTenantResourceConfig(tenantId);
        return configMap.get(resourceCode);
    }
}
