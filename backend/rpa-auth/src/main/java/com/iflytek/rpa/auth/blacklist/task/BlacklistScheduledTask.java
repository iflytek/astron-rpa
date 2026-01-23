package com.iflytek.rpa.auth.blacklist.task;

import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * 黑名单定时任务
 * 自动解封已过期的用户（兜底机制）
 *
 * 说明：
 * 1. 主要采用懒加载机制：在查询时（isBlocked）自动检查并更新过期状态
 * 2. 定时任务作为兜底：每天凌晨执行一次，处理可能遗漏的过期记录
 * 3. 作用：
 *    - 更新数据库 status 字段：1（生效中）-> 0（已解封）
 *    - 清理 Redis 中可能残留的缓存
 *    - 保持数据库和 Redis 的数据一致性
 *    - 容错：处理长时间未访问的用户记录
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
@Component
@RequiredArgsConstructor
@ConditionalOnProperty(prefix = "blacklist.task", name = "enabled", havingValue = "true", matchIfMissing = true)
public class BlacklistScheduledTask {

    private final BlackListService blackListService;

    /**
     * 定时解封已过期的用户
     * 每天凌晨 2 点执行一次
     *
     * 注意：主要依赖懒加载机制，定时任务仅作为兜底
     * 懒加载在 isBlocked() 方法中实现，查询时自动检查并更新过期状态
     */
    @Scheduled(cron = "${blacklist.task.unban-cron:0 0 2 * * ?}")
    public void unbanExpiredUsers() {
        log.info("开始执行定时解封任务");

        try {
            int count = blackListService.batchUnbanExpired();
            log.info("定时解封任务完成，共解封 {} 个用户", count);
        } catch (Exception e) {
            log.error("定时解封任务执行失败", e);
        }
    }

    /**
     * 定时清理过期数据
     * 每天凌晨 2 点执行
     * 可选：删除超过 90 天的已解封记录
     */
    @Scheduled(cron = "${blacklist.task.cleanup-cron:0 0 2 * * ?}")
    public void cleanupExpiredData() {
        log.info("开始执行黑名单数据清理任务");

        try {
            // TODO: 实现清理逻辑（可选）
            // 例如：删除 90 天前的已解封记录
            log.info("黑名单数据清理任务完成");
        } catch (Exception e) {
            log.error("黑名单数据清理任务执行失败", e);
        }
    }
}
