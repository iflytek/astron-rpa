package com.iflytek.rpa.auth.sp.uap.utils;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

/**
 * UAP Token 工具类
 * 使用与UAP兼容的JDK序列化方式存储和读取token
 *
 * @author lihang
 * @date 2025-11-30
 */
@Slf4j
@Component
@ConditionalOnSaaSOrUAP
public class UapTokenUtils {

    /**
     * accessToken 过期时间：2小时（7200秒）
     */
    public static final long ACCESS_TOKEN_EXPIRE_SECONDS = 7200L;

    /**
     * refreshToken 过期时间：7天（604800秒）
     */
    public static final long REFRESH_TOKEN_EXPIRE_SECONDS = 604800L;

    /**
     * refreshToken 续期阈值：1天（86400秒）
     * 当 refreshToken 剩余 TTL 小于此值时，进行续期
     */
    public static final long REFRESH_TOKEN_RENEWAL_THRESHOLD_SECONDS = 86400L;

    private static RedisTemplate<String, Object> uapRedisTemplate;

    /**
     * 注入UAP兼容的RedisTemplate
     */
    @Autowired
    @Qualifier("uapCompatibleRedisTemplate")
    public void setUapRedisTemplate(RedisTemplate<String, Object> template) {
        UapTokenUtils.uapRedisTemplate = template;
    }

    /**
     * 保存 accessToken 到 Redis
     *
     * @param sessionId session ID
     * @param accessToken 访问令牌
     * @param expireSeconds 过期时间（秒）
     */
    public static void saveAccessToken(String sessionId, String accessToken, long expireSeconds) {
        try {
            String key = "uap:user:access:token:" + sessionId;
            uapRedisTemplate.opsForValue().set(key, accessToken, expireSeconds, TimeUnit.SECONDS);
            log.info("已保存 accessToken 到 Redis, key: {}, 过期时间: {}秒", key, expireSeconds);
        } catch (Exception e) {
            log.error("保存 accessToken 失败", e);
        }
    }

    /**
     * 保存 refreshToken 到 Redis
     *
     * @param sessionId session ID
     * @param refreshToken 刷新令牌
     * @param expireSeconds 过期时间（秒）
     */
    public static void saveRefreshToken(String sessionId, String refreshToken, long expireSeconds) {
        try {
            String key = "uap:user:refresh:token:" + sessionId;
            uapRedisTemplate.opsForValue().set(key, refreshToken, expireSeconds, TimeUnit.SECONDS);
            log.info("已保存 refreshToken 到 Redis, key: {}, 过期时间: {}秒", key, expireSeconds);
        } catch (Exception e) {
            log.error("保存 refreshToken 失败", e);
        }
    }

    /**
     * 获取 accessToken
     *
     * @param sessionId session ID
     * @return accessToken
     */
    public static String getAccessToken(String sessionId) {
        try {
            String key = "uap:user:access:token:" + sessionId;
            Object value = uapRedisTemplate.opsForValue().get(key);
            return value != null ? value.toString() : null;
        } catch (Exception e) {
            log.error("获取 accessToken 失败", e);
            return null;
        }
    }

    /**
     * 获取 refreshToken
     *
     * @param sessionId session ID
     * @return refreshToken
     */
    public static String getRefreshToken(String sessionId) {
        try {
            String key = "uap:user:refresh:token:" + sessionId;
            Object value = uapRedisTemplate.opsForValue().get(key);
            return value != null ? value.toString() : null;
        } catch (Exception e) {
            log.error("获取 refreshToken 失败", e);
            return null;
        }
    }

    /**
     * 获取 refreshToken 的剩余过期时间（TTL）
     *
     * @param sessionId session ID
     * @return 剩余过期时间（秒），-1 表示 key 不存在，-2 表示 key 存在但没有设置过期时间
     */
    public static long getRefreshTokenTTL(String sessionId) {
        try {
            String key = "uap:user:refresh:token:" + sessionId;
            Long ttl = uapRedisTemplate.getExpire(key, TimeUnit.SECONDS);
            if (ttl == null) {
                return -1; // key 不存在
            }
            return ttl;
        } catch (Exception e) {
            log.error("获取 refreshToken TTL 失败", e);
            return -1;
        }
    }

    /**
     * 续期 refreshToken（延长 TTL，不替换 value）
     * 仅在 refreshToken 存在且剩余 TTL 小于阈值时进行续期
     *
     * @param sessionId session ID
     * @return 是否续期成功
     */
    public static boolean renewRefreshToken(String sessionId) {
        try {
            String key = "uap:user:refresh:token:" + sessionId;

            // 检查 key 是否存在
            if (!Boolean.TRUE.equals(uapRedisTemplate.hasKey(key))) {
                log.debug("refreshToken 不存在，无需续期, sessionId: {}", sessionId);
                return false;
            }

            // 获取当前剩余 TTL
            Long currentTTL = uapRedisTemplate.getExpire(key, TimeUnit.SECONDS);
            if (currentTTL == null || currentTTL < 0) {
                log.debug("refreshToken TTL 无效，无法续期, sessionId: {}, TTL: {}", sessionId, currentTTL);
                return false;
            }

            // 仅在剩余 TTL 小于阈值时续期
            if (currentTTL < REFRESH_TOKEN_RENEWAL_THRESHOLD_SECONDS) {
                uapRedisTemplate.expire(key, REFRESH_TOKEN_EXPIRE_SECONDS, TimeUnit.SECONDS);
                log.info(
                        "已续期 refreshToken, sessionId: {}, 原剩余时间: {}秒, 续期后: {}秒",
                        sessionId,
                        currentTTL,
                        REFRESH_TOKEN_EXPIRE_SECONDS);
                return true;
            } else {
                log.debug("refreshToken 剩余时间充足，无需续期, sessionId: {}, 剩余时间: {}秒", sessionId, currentTTL);
                return false;
            }
        } catch (Exception e) {
            log.error("续期 refreshToken 失败, sessionId: {}", sessionId, e);
            return false;
        }
    }

    /**
     * 删除用户的所有 token
     *
     * @param sessionId session ID
     */
    public static void deleteTokens(String sessionId) {
        try {
            String accessTokenKey = "uap:user:access:token:" + sessionId;
            String refreshTokenKey = "uap:user:refresh:token:" + sessionId;
            uapRedisTemplate.delete(accessTokenKey);
            uapRedisTemplate.delete(refreshTokenKey);
            log.info("已删除 sessionId: {} 的所有 token", sessionId);
        } catch (Exception e) {
            log.error("删除 token 失败", e);
        }
    }
}
