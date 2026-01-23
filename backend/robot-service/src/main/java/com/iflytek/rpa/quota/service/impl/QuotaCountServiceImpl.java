package com.iflytek.rpa.quota.service.impl;

import com.iflytek.rpa.market.dao.AppMarketUserDao;
import com.iflytek.rpa.quota.service.QuotaCountService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 配额数量查询服务实现类
 * 提供各种资源的当前数量查询（带缓存）
 */
@Slf4j
@Service
public class QuotaCountServiceImpl implements QuotaCountService {
    @Autowired
    private RobotDesignDao robotDesignDao;

    @Autowired
    private AppMarketUserDao appMarketUserDao;

    @Override
    public Integer getDesignerCount(String tenantId, String userId) {
        if (StringUtils.isBlank(tenantId) || StringUtils.isBlank(userId)) {
            return 0;
        }
        // 从数据库查询
        try {
            // 查询用户在当前租户下创建的机器人数量（未删除的）
            com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<com.iflytek.rpa.robot.entity.RobotDesign>
                    wrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<
                                    com.iflytek.rpa.robot.entity.RobotDesign>()
                            .eq(com.iflytek.rpa.robot.entity.RobotDesign::getTenantId, tenantId)
                            .eq(com.iflytek.rpa.robot.entity.RobotDesign::getCreatorId, userId)
                            .eq(com.iflytek.rpa.robot.entity.RobotDesign::getDeleted, 0);
            Integer count = robotDesignDao.selectCount(wrapper);
            Integer result = count != null ? count : 0;

            return result;
        } catch (Exception e) {
            log.error("查询设计器数量失败，tenantId: {}, userId: {}", tenantId, userId, e);
            return 0;
        }
    }

    @Override
    public Integer getMarketJoinCount(String tenantId, String userId) {
        if (StringUtils.isBlank(tenantId) || StringUtils.isBlank(userId)) {
            return 0;
        }
        // 从数据库查询
        try {
            // 查询用户在当前租户下已加入的市场数量（未删除的）
            Integer count = appMarketUserDao.getMarketJoinCount(tenantId, userId);
            Integer result = count != null ? count : 0;
            return result;
        } catch (Exception e) {
            log.error("查询市场加入数量失败，tenantId: {}, userId: {}", tenantId, userId, e);
            return 0;
        }
    }
}
