package com.iflytek.rpa.auth.sp.casdoor.utils;

import com.iflytek.rpa.auth.exception.NoLoginException;
import com.iflytek.rpa.auth.utils.RedisUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

/**
 * @desc: Casdoor Token管理器，仅在casdoor profile下生效
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 10:29
 */
@Component
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class TokenManager {

    private static final Logger logger = LoggerFactory.getLogger(TokenManager.class);

    private static final String ACCESS_TOKEN_PREFIX = "auth:token:access:";
    private static final String REFRESH_TOKEN_PREFIX = "auth:token:refresh:";

    /**
     * 获取用户的AccessToken（用于服务端调用Casdoor API）
     *
     * @param username 用户名
     * @return AccessToken，如果不存在返回null
     */
    public static String getAccessToken(String username) {
        if (username == null || username.trim().isEmpty()) {
            return null;
        }

        String key = ACCESS_TOKEN_PREFIX + username;
        Object token = RedisUtils.get(key);
        return token != null ? token.toString() : null;
    }

    /**
     * 获取用户的RefreshToken（用于服务端刷新token）
     *
     * @param username 用户名
     * @return RefreshToken，如果不存在返回null
     */
    public static String getRefreshToken(String username) {
        if (username == null || username.trim().isEmpty()) {
            return null;
        }

        String key = REFRESH_TOKEN_PREFIX + username;
        Object token = RedisUtils.get(key);
        return token != null ? token.toString() : null;
    }

    /**
     * 存储用户的token到Redis
     *
     * @param username 用户名
     * @param accessToken AccessToken
     * @param refreshToken RefreshToken
     * @param expireTime 过期时间（秒）
     */
    public static void storeTokens(String username, String accessToken, String refreshToken, long expireTime) {
        if (username == null || username.trim().isEmpty()) {
            logger.warn("用户名为空，无法存储token");
            return;
        }

        String accessTokenKey = ACCESS_TOKEN_PREFIX + username;
        String refreshTokenKey = REFRESH_TOKEN_PREFIX + username;

        RedisUtils.set(accessTokenKey, accessToken, expireTime);
        RedisUtils.set(refreshTokenKey, refreshToken, expireTime);

        logger.debug("用户 {} 的服务端token已存储到Redis", username);
    }

    /**
     * 清除用户的token
     *
     * @param username 用户名
     */
    public static void clearTokens(String username) {
        if (username == null || username.trim().isEmpty()) {
            logger.warn("用户名为空，无法清除token");
            return;
        }

        String accessTokenKey = ACCESS_TOKEN_PREFIX + username;
        String refreshTokenKey = REFRESH_TOKEN_PREFIX + username;

        RedisUtils.del(accessTokenKey, refreshTokenKey);

        logger.debug("用户 {} 的服务端token已从Redis中清除", username);
    }

    /**
     * 检查用户的token是否存在
     *
     * @param username 用户名
     * @return true如果AccessToken存在，false否则
     */
    public static boolean hasToken(String username) {
        if (username == null || username.trim().isEmpty()) {
            return false;
        }

        String accessTokenKey = ACCESS_TOKEN_PREFIX + username;
        return RedisUtils.hasKey(accessTokenKey);
    }

    /**
     * 获取当前登录用户的AccessToken（便捷方法，供其他服务使用）
     *
     * @return 当前用户的AccessToken
     * @throws NoLoginException 如果用户未登录
     */
    public static String getCurrentUserAccessToken() throws NoLoginException {
        //        todo 补充以下代码！！！
        //        User currentUser = UserUtils.nowLoginUser();
        //        String accessToken = getAccessToken(currentUser.name);
        //
        //        if (accessToken == null) {
        //            throw new NoLoginException("用户AccessToken不存在，请重新登录");
        //        }
        //
        //        return accessToken;
        return null;
    }
}
