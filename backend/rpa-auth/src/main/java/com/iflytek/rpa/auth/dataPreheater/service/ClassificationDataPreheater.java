package com.iflytek.rpa.auth.dataPreheater.service;

import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.dataPreheater.dao.AppMarketClassificationDao;
import com.iflytek.rpa.auth.dataPreheater.entity.InitDataEvent;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * 应用市场-分类
 */
@Component
@Slf4j
public class ClassificationDataPreheater {

    @Autowired
    private AppMarketClassificationDao appMarketClassificationDao;

    @Autowired
    private TenantService tenantService;

    @EventListener(classes = {ApplicationReadyEvent.class, InitDataEvent.class})
    @Transactional(rollbackFor = Exception.class)
    public void importClassification(Object event) throws Exception {
        log.info("-----------------开始导入分类数据-----------------");
        AppResponse<List<String>> noClassifyTenantIds = tenantService.getNoClassifyTenantIds();
        List<String> tenantIds = new ArrayList<>();
        if (Objects.nonNull(noClassifyTenantIds) && noClassifyTenantIds.ok() && noClassifyTenantIds.getData() != null) {
            tenantIds = noClassifyTenantIds.getData();
        }

        for (String tenantId : tenantIds) {
            // 基于行数对数据表预查询避免重复插入
            Integer dataCount = appMarketClassificationDao.countByTenantId(tenantId);
            if (dataCount > 0) {
                continue;
            }

            Integer i = appMarketClassificationDao.insertDefaultClassification(tenantId);
            log.info("租户[{}]分类数据导入完成，导入条数：{}", tenantId, i);
        }
        if (!tenantIds.isEmpty()) {
            // 通过Feign调用rpa-auth服务更新租户分类标志
            AppResponse<Integer> updateResponse = tenantService.updateTenantClassifyCompleted(tenantIds);
            Integer i = -1;
            if (Objects.nonNull(updateResponse) && updateResponse.ok() && updateResponse.getData() != null) {
                i = updateResponse.getData();
            }

            if (i != tenantIds.size()) {
                throw new RuntimeException("分类数据导入异常，请检查！");
            }
        }
        log.info("-----------------分类数据导入完成-----------------");
    }
}
