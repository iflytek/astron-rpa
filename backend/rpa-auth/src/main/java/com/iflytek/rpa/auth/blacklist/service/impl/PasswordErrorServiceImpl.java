package com.iflytek.rpa.auth.blacklist.service.impl;

import com.iflytek.rpa.auth.blacklist.config.BlacklistConfig;
import com.iflytek.rpa.auth.blacklist.exception.ShouldBeBlackException;
import com.iflytek.rpa.auth.blacklist.service.PasswordErrorService;
import com.iflytek.rpa.auth.utils.RedisUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * 密码错误计数服务实现
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PasswordErrorServiceImpl implements PasswordErrorService {

    private final BlacklistConfig blacklistConfig;

    @Override
    public int recordPasswordError(String userId, String username) {
        String key = BlacklistConfig.getPasswordErrorKey(userId);

        // 递增错误计数
        long count = RedisUtils.incr(key, 1);

        // 设置过期时间（首次设置）
        if (count == 1) {
            RedisUtils.expire(key, blacklistConfig.getPasswordErrorExpire());
        }

        log.warn(
                "用户密码错误，userId: {}, username: {}, 当前错误次数: {}/{}",
                userId,
                username,
                count,
                blacklistConfig.getPasswordErrorLimit());

        // 检查是否达到阈值
        if (count >= blacklistConfig.getPasswordErrorLimit()) {
            log.error("用户密码错误次数达到阈值，触发封禁，userId: {}, username: {}, 错误次数: {}", userId, username, count);

            // 清除计数
            RedisUtils.del(key);

            // 抛出封禁异常
            throw new ShouldBeBlackException(
                    userId,
                    username,
                    "密码错误次数过多（" + blacklistConfig.getPasswordErrorLimit() + "次）",
                    ShouldBeBlackException.BlackType.PASSWORD_ERROR);
        }

        return (int) count;
    }

    @Override
    public void clearPasswordError(String userId) {
        String key = BlacklistConfig.getPasswordErrorKey(userId);
        RedisUtils.del(key);
        log.debug("清除密码错误记录，userId: {}", userId);
    }

    @Override
    public int getPasswordErrorCount(String userId) {
        String key = BlacklistConfig.getPasswordErrorKey(userId);
        Object count = RedisUtils.get(key);
        return count != null ? Integer.parseInt(count.toString()) : 0;
    }
}
