package com.iflytek.rpa.base.security;

import com.iflytek.rpa.utils.IpUtil;
import com.iflytek.rpa.utils.RedisUtils;
import com.iflytek.rpa.utils.exception.ServiceException;
import com.iflytek.rpa.utils.response.ErrorCodeEnum;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import javax.servlet.http.HttpServletRequest;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 原子能力写接口的访问控制。
 *
 * <p>{@code /atom/add-common}、{@code /atom/update-common}、{@code /atom/save-atomics}
 * 改写的是整个平台共用的原子能力定义，但网关对 {@code /api/robot/} 默认不做会话认证
 * （见 {@code docker/volumes/nginx/default.conf}，为避免与认证服务循环调用），
 * 因此这几个接口需要自己校验身份并限流，见 issue #790。</p>
 *
 * <p>默认拒绝：没有配置 {@code atom.admin.token} 时写接口一律拒绝，而不是放行。</p>
 */
@Component
public class AtomAdminAccessGuard {

    public static final String TOKEN_HEADER = "X-Atom-Admin-Token";

    private static final Logger logger = LoggerFactory.getLogger(AtomAdminAccessGuard.class);
    private static final String RATE_LIMIT_KEY_PREFIX = "rpa:atom:admin:rate:";

    @Value("${atom.admin.token:}")
    private String adminToken;

    @Value("${atom.admin.rate-limit.max-requests:20}")
    private int maxRequests;

    @Value("${atom.admin.rate-limit.window-seconds:60}")
    private long windowSeconds;

    /**
     * 校验一次原子能力写请求，不通过直接抛出 {@link ServiceException}。
     */
    public void checkWriteAccess(HttpServletRequest request) {
        String clientIp = IpUtil.getIpAddr(request);

        // 先限流再验令牌，令牌本身也就不会被无限次尝试
        enforceRateLimit(clientIp);
        verifyToken(request, clientIp);
    }

    private void verifyToken(HttpServletRequest request, String clientIp) {
        if (StringUtils.isBlank(adminToken)) {
            logger.warn("原子能力写接口被访问但未配置 atom.admin.token, 已拒绝, clientIp: {}", clientIp);
            throw new ServiceException(ErrorCodeEnum.E_NO_POWER.getCode(), "原子能力写接口未启用：请先配置 atom.admin.token");
        }

        String presented = request.getHeader(TOKEN_HEADER);
        if (StringUtils.isBlank(presented) || !constantTimeEquals(presented, adminToken)) {
            logger.warn("原子能力写接口令牌校验失败, clientIp: {}", clientIp);
            throw new ServiceException(ErrorCodeEnum.E_NO_POWER.getCode(), "原子能力写接口令牌校验失败");
        }
    }

    private void enforceRateLimit(String clientIp) {
        if (maxRequests <= 0 || windowSeconds <= 0) {
            return;
        }

        String key = RATE_LIMIT_KEY_PREFIX + StringUtils.defaultIfBlank(clientIp, "unknown");
        long count;
        try {
            count = RedisUtils.incr(key, 1);
            if (count == 1 || RedisUtils.getExpire(key) < 0) {
                // 计数器必须带过期时间，否则一个窗口的计数会把调用方永久挡在门外
                RedisUtils.expire(key, windowSeconds);
            }
        } catch (Exception e) {
            // Redis 不可用时不阻断：令牌校验才是这里真正的门禁，限流是纵深防御
            logger.warn("原子能力写接口限流计数失败，本次跳过限流, clientIp: {}", clientIp, e);
            return;
        }

        if (count > maxRequests) {
            logger.warn("原子能力写接口触发限流, clientIp: {}, count: {}", clientIp, count);
            throw new ServiceException(ErrorCodeEnum.E_SERVICE_POWER_LIMIT.getCode(), "请求过于频繁，请稍后再试");
        }
    }

    private boolean constantTimeEquals(String presented, String expected) {
        return MessageDigest.isEqual(
                presented.getBytes(StandardCharsets.UTF_8), expected.getBytes(StandardCharsets.UTF_8));
    }
}
