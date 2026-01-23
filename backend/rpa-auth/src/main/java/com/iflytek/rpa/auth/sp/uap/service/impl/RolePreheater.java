package com.iflytek.rpa.auth.sp.uap.service.impl;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.AppInfoBo;
import com.iflytek.rpa.auth.sp.uap.dao.RoleDao;
import com.iflytek.rpa.auth.sp.uap.dao.TenantDao;
import java.util.List;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 启动检查是否有角色【未指定】
 */
@Slf4j
@Component
@ConditionalOnSaaSOrUAP
public class RolePreheater implements CommandLineRunner {

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Resource
    private RoleDao roleDao;

    @Autowired
    private TenantDao tenantDao;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void run(String... args) throws Exception {
        log.info("-----------------开始检查角色【未指定】-----------------");
        // 检查 t_uap_role
        Integer exist = roleDao.getUnspecifiedRole(databaseName);
        // 查appId 和appName
        if (exist <= 0) {
            AppInfoBo info = roleDao.selectAppInfo(databaseName);
            String appId = info.getAppId();
            String appName = info.getAppName(); // 拿不到appId
            if (StringUtils.isBlank(appId)) {
                return;
            }
            // 插入角色【未指定】
            roleDao.insertUnspecifiedRole(databaseName, appId, appName);
        }

        List<String> tenantIds = tenantDao.getAllTenantId(databaseName);
        for (String tenantId : tenantIds) {
            // 该租户是否存在角色【未指定】
            Integer j = roleDao.getUnspecifiedRoleWithTenant(databaseName, tenantId);
            if (j <= 0) {
                roleDao.insertUnspecifiedTenantBind(databaseName, tenantId);
            }
        }
        log.info("-----------------结束检查角色【未指定】-----------------");
    }
}
