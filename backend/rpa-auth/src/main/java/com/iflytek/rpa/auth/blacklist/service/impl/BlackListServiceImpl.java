package com.iflytek.rpa.auth.blacklist.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.blacklist.config.BlacklistConfig;
import com.iflytek.rpa.auth.blacklist.dao.UserBlacklistDao;
import com.iflytek.rpa.auth.blacklist.dto.BlacklistCacheDto;
import com.iflytek.rpa.auth.blacklist.entity.UserBlacklist;
import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import com.iflytek.rpa.auth.utils.RedisUtils;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 黑名单服务实现类
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class BlackListServiceImpl implements BlackListService {

    private final UserBlacklistDao userBlacklistDao;
    private final BlacklistConfig blacklistConfig;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 分布式锁前缀
     */
    private static final String LOCK_PREFIX = "LOCK:BL:";

    @Override
    @Transactional(rollbackFor = Exception.class)
    public UserBlacklist add(String userId, String username, String reason, String operator) {
        log.info("开始添加黑名单，userId: {}, username: {}, reason: {}, operator: {}", userId, username, reason, operator);

        // 使用分布式锁，避免并发问题
        String lockKey = LOCK_PREFIX + userId;
        try {
            boolean lockSuccess = tryLock(lockKey, 10);
            if (!lockSuccess) {
                log.warn("获取分布式锁失败，userId: {}", userId);
                throw new RuntimeException("系统繁忙，请稍后再试");
            }

            // 查询当前是否有生效的封禁记录
            UserBlacklist existingBlacklist = userBlacklistDao.findActiveBlacklist(userId);

            UserBlacklist blacklist;
            if (existingBlacklist != null) {
                // 已有封禁记录，升级封禁等级
                log.info(
                        "用户已在黑名单中，升级封禁等级，当前等级: {}, 次数: {}",
                        existingBlacklist.getBanLevel(),
                        existingBlacklist.getBanCount());

                int newLevel = existingBlacklist.getBanLevel() + 1;
                int newCount = existingBlacklist.getBanCount() + 1;
                Long newDuration = blacklistConfig.getDurationByLevel(newLevel);

                existingBlacklist.setBanLevel(newLevel);
                existingBlacklist.setBanCount(newCount);
                existingBlacklist.setBanDuration(newDuration);
                existingBlacklist.setBanReason(reason);
                existingBlacklist.setStartTime(LocalDateTime.now());
                existingBlacklist.setEndTime(LocalDateTime.now().plusSeconds(newDuration));
                existingBlacklist.setOperator(operator);

                userBlacklistDao.updateById(existingBlacklist);
                blacklist = existingBlacklist;

                log.info("黑名单升级成功，新等级: {}, 新次数: {}, 封禁至: {}", newLevel, newCount, blacklist.getEndTime());
            } else {
                // 新增封禁记录
                Long duration = blacklistConfig.getDurationByLevel(1);
                blacklist = UserBlacklist.builder()
                        .userId(userId)
                        .username(username)
                        .banReason(reason)
                        .banLevel(1)
                        .banCount(1)
                        .banDuration(duration)
                        .startTime(LocalDateTime.now())
                        .endTime(LocalDateTime.now().plusSeconds(duration))
                        .status(1)
                        .operator(operator)
                        .build();

                userBlacklistDao.insert(blacklist);

                log.info("新增黑名单成功，封禁至: {}", blacklist.getEndTime());
            }

            // 写入 Redis 缓存
            cacheBlacklist(blacklist);

            return blacklist;
        } finally {
            // 释放锁
            unlock(lockKey);
        }
    }

    @Override
    public BlacklistCacheDto isBlocked(String userId) {
        if (userId == null || userId.isEmpty()) {
            return null;
        }

        String key = BlacklistConfig.getBlacklistKey(userId);

        try {
            // 优先从 Redis 查询
            // 如果 Redis 中存在 key，说明用户肯定还在封禁中（TTL 就是根据 endTime 设置的）
            Object cached = RedisUtils.get(key);
            if (cached != null) {
                // Redis 中存在，说明用户在黑名单中，直接返回
                BlacklistCacheDto dto = objectMapper.convertValue(cached, BlacklistCacheDto.class);
                log.debug("从 Redis 查询到黑名单信息，userId: {}", userId);
                return dto;
            }

            // Redis 中不存在，查询数据库
            //            UserBlacklist blacklist = userBlacklistDao.findActiveBlacklist(userId);
            UserBlacklist blacklist = null;
            if (blacklist != null) {
                LocalDateTime now = LocalDateTime.now();
                if (blacklist.getEndTime().isAfter(now)) {
                    // 数据库中存在且未过期，回填 Redis
                    log.info("从数据库查询到黑名单信息，回填 Redis，userId: {}", userId);
                    cacheBlacklist(blacklist);
                    return buildCacheDto(blacklist);
                } else {
                    // 已过期，懒加载自动解封（更新数据库状态）
                    log.info("黑名单已过期，懒加载自动解封，userId: {}", userId);
                    unbanIfExpired(userId);
                }
            }

            return null;
        } catch (Exception e) {
            log.error("查询黑名单失败，userId: {}", userId, e);
            // 异常时返回 null，不查询数据库，避免影响性能
            return null;
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void unbanIfExpired(String userId) {
        UserBlacklist blacklist = userBlacklistDao.findActiveBlacklist(userId);
        if (blacklist != null && blacklist.getEndTime().isBefore(LocalDateTime.now())) {
            userBlacklistDao.unban(blacklist.getId());
            String key = BlacklistConfig.getBlacklistKey(userId);
            RedisUtils.del(key);
            log.info("自动解封用户，userId: {}", userId);
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean unban(String userId, String operator) {
        log.info("手动解封用户，userId: {}, operator: {}", userId, operator);

        LambdaQueryWrapper<UserBlacklist> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(UserBlacklist::getUserId, userId)
                .eq(UserBlacklist::getStatus, 1)
                .orderByDesc(UserBlacklist::getCreateTime)
                .last("LIMIT 1");

        UserBlacklist blacklist = userBlacklistDao.selectOne(wrapper);
        if (blacklist != null) {
            userBlacklistDao.unban(blacklist.getId());
            String key = BlacklistConfig.getBlacklistKey(userId);
            RedisUtils.del(key);
            log.info("手动解封成功，userId: {}", userId);
            return true;
        }

        log.warn("未找到生效的黑名单记录，userId: {}", userId);
        return false;
    }

    @Override
    public List<UserBlacklist> getHistory(String userId) {
        return userBlacklistDao.findHistoryByUserId(userId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public int batchUnbanExpired() {
        log.info("开始批量解封已过期用户");

        // 每次处理 100 条
        List<UserBlacklist> expiredList = userBlacklistDao.findExpiredBlacklist(LocalDateTime.now(), 100);

        int count = 0;
        for (UserBlacklist blacklist : expiredList) {
            try {
                userBlacklistDao.unban(blacklist.getId());
                String key = BlacklistConfig.getBlacklistKey(blacklist.getUserId());
                RedisUtils.del(key);
                count++;
                log.info("解封过期用户，userId: {}, username: {}", blacklist.getUserId(), blacklist.getUsername());
            } catch (Exception e) {
                log.error("解封用户失败，userId: {}", blacklist.getUserId(), e);
            }
        }

        log.info("批量解封完成，共解封 {} 个用户", count);
        return count;
    }

    @Override
    public void forceLogout(HttpServletRequest request, HttpServletResponse response) {
        log.info("强制注销用户会话");
        try {
            // 调用 UAP API 注销会话，从 request 中清除会话信息
            com.iflytek.sec.uap.client.api.UapUserInfoAPI.logout(request, response);
            log.info("用户会话已注销");
        } catch (Exception e) {
            log.error("注销用户会话失败", e);
        }
    }

    /**
     * 缓存黑名单到 Redis
     */
    private void cacheBlacklist(UserBlacklist blacklist) {
        try {
            String key = BlacklistConfig.getBlacklistKey(blacklist.getUserId());
            BlacklistCacheDto dto = buildCacheDto(blacklist);

            // 计算剩余时间（秒）
            long ttl = dto.getRemainingSeconds();
            if (ttl > 0) {
                RedisUtils.set(key, dto, ttl);
                log.debug("黑名单已缓存到 Redis，userId: {}, ttl: {}秒", blacklist.getUserId(), ttl);
            }
        } catch (Exception e) {
            log.error("缓存黑名单到 Redis 失败，userId: {}", blacklist.getUserId(), e);
        }
    }

    /**
     * 构建缓存 DTO
     */
    private BlacklistCacheDto buildCacheDto(UserBlacklist blacklist) {
        long remainingSeconds =
                Duration.between(LocalDateTime.now(), blacklist.getEndTime()).getSeconds();
        if (remainingSeconds < 0) {
            remainingSeconds = 0;
        }

        // 将 LocalDateTime 转换为时间戳（毫秒），避免序列化问题
        long endTimeMillis = blacklist
                .getEndTime()
                .atZone(java.time.ZoneId.systemDefault())
                .toInstant()
                .toEpochMilli();

        return BlacklistCacheDto.builder()
                .userId(blacklist.getUserId())
                .username(blacklist.getUsername())
                .reason(blacklist.getBanReason())
                .level(blacklist.getBanLevel())
                .count(blacklist.getBanCount())
                .endTimeMillis(endTimeMillis)
                .remainingSeconds(remainingSeconds)
                .build();
    }

    /**
     * 尝试获取分布式锁（简单实现）
     */
    private boolean tryLock(String key, long expireSeconds) {
        try {
            return RedisUtils.redisTemplate.opsForValue().setIfAbsent(key, "locked", Duration.ofSeconds(expireSeconds));
        } catch (Exception e) {
            log.error("获取分布式锁失败", e);
            return false;
        }
    }

    /**
     * 释放分布式锁
     */
    private void unlock(String key) {
        try {
            RedisUtils.del(key);
        } catch (Exception e) {
            log.error("释放分布式锁失败", e);
        }
    }
}
