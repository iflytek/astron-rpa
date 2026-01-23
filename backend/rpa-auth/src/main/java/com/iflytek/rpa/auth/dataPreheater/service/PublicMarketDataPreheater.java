package com.iflytek.rpa.auth.dataPreheater.service;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.dataPreheater.dao.AppMarketDao;
import com.iflytek.rpa.auth.dataPreheater.dao.AppMarketUserDao;
import com.iflytek.rpa.auth.dataPreheater.entity.AppMarket;
import com.iflytek.rpa.auth.dataPreheater.entity.AppMarketUser;
import com.iflytek.rpa.auth.dataPreheater.entity.InitDataEvent;
import com.iflytek.rpa.auth.dataPreheater.entity.MarketTypeEnum;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.IdWorker;
import com.iflytek.rpa.auth.utils.ListBatchUtil;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 企业公共市场-用户数据导入
 */
@Slf4j
@Component
@ConditionalOnSaaSOrUAP
public class PublicMarketDataPreheater {
    @Autowired
    private AppMarketDao appMarketDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private TenantService tenantService;

    @EventListener(classes = {ApplicationReadyEvent.class, InitDataEvent.class})
    @Transactional(rollbackFor = Exception.class)
    public void importPublicMarketData(Object event) throws Exception {
        // 企业版 生成 企业团队市场
        // 通过Feign调用rpa-auth服务获取所有企业租户ID列表
        AppResponse<List<String>> allEnterpriseTenantId = tenantService.getAllEnterpriseTenantId();
        List<String> tenantIds = new ArrayList<>();
        if (Objects.nonNull(allEnterpriseTenantId)
                && allEnterpriseTenantId.ok()
                && allEnterpriseTenantId.getData() != null) {
            tenantIds = allEnterpriseTenantId.getData();
        }

        if (tenantIds.isEmpty()) {
            return;
        }
        for (String tenantId : tenantIds) {
            // 检查 企业 公共市场是否存在
            AppMarket publicMarket = appMarketDao.selectPublicMarket(tenantId);
            if (null == publicMarket) {
                AppMarket appMarket = new AppMarket();

                // 增加租户管理员账号
                AppResponse<List<String>> tenantManagerIds = tenantService.getTenantManagerIds(tenantId);
                List<String> marketManagerUserIds = new ArrayList<>();
                if (Objects.nonNull(tenantManagerIds) && tenantManagerIds.ok() && tenantManagerIds.getData() != null) {
                    marketManagerUserIds = tenantManagerIds.getData();
                }

                if (marketManagerUserIds.isEmpty()) {
                    throw new RuntimeException("租户无管理员");
                }
                String first = marketManagerUserIds.get(0);

                // 新增市场
                String marketName = "企业公共市场";
                appMarket.setMarketName(marketName);
                appMarket.setCreatorId(first);
                appMarket.setMarketType(MarketTypeEnum.PUBLIC.getCode());
                appMarket.setUpdaterId(first);
                String marketId = idWorker.nextId() + "";
                appMarket.setMarketId(marketId);
                appMarket.setTenantId(tenantId);
                appMarketDao.addMarketWithType(appMarket);

                // 拥有者
                AppMarketUser appMarketUser = new AppMarketUser();
                appMarketUser.setMarketId(marketId);
                appMarketUser.setCreatorId(first);
                appMarketUser.setUpdaterId(first);
                appMarketUserDao.addDefaultUser(appMarketUser);

                // 管理员新增
                for (String marketManagerUserId : marketManagerUserIds) {
                    AppMarketUser marketUser = new AppMarketUser();
                    marketUser.setMarketId(marketId);
                    marketUser.setCreatorId(marketManagerUserId);
                    marketUser.setUpdaterId(marketManagerUserId);
                    marketUser.setUserType("admin");
                    appMarketUserDao.addUser(marketUser);
                }

                normalUserHandle(tenantId, marketId);
            } else {
                normalUserHandle(tenantId, publicMarket.getMarketId());
            }
        }
    }

    private void normalUserHandle(String tenantId, String marketId) {
        // 通过Feign调用rpa-auth服务获取租户普通用户ID列表
        AppResponse<List<String>> tenantNormalUserIds = tenantService.getTenantNormalUserIds(tenantId);
        List<String> userVoList = new ArrayList<>();
        if (Objects.nonNull(tenantNormalUserIds) && tenantNormalUserIds.ok() && tenantNormalUserIds.getData() != null) {
            userVoList = tenantNormalUserIds.getData();
        }

        List<String> existUserId = appMarketUserDao.getAllUserId(tenantId, marketId);

        List<String> preInsertUserIds =
                userVoList.stream().filter(u -> !existUserId.contains(u)).collect(Collectors.toList());

        if (preInsertUserIds.isEmpty()) {
            return;
        }

        List<AppMarketUser> preInsert = getPreInsert(tenantId, preInsertUserIds, marketId);

        ListBatchUtil.process(preInsert, 300, insertBatchList -> {
            appMarketUserDao.insertBatch(insertBatchList);
        });
    }

    private List<AppMarketUser> getPreInsert(String tenantId, List<String> preInsertUserIds, String marketId) {
        List<AppMarketUser> preInsert = new ArrayList<>();
        if (preInsertUserIds.isEmpty()) {
            return preInsert;
        }
        for (String userId : preInsertUserIds) {
            AppMarketUser appMarketUser = new AppMarketUser();
            appMarketUser.setMarketId(marketId);
            appMarketUser.setCreatorId(userId);
            appMarketUser.setUpdaterId(userId);
            appMarketUser.setUserType("acquirer");
            appMarketUser.setDeleted(0);
            preInsert.add(appMarketUser);
        }
        return preInsert;
    }
}
