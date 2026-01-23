package com.iflytek.rpa.auth.blacklist.aspect;

import com.iflytek.rpa.auth.blacklist.dto.BlacklistCacheDto;
import com.iflytek.rpa.auth.blacklist.exception.ShouldBeBlackException;
import com.iflytek.rpa.auth.blacklist.exception.UserBlockedException;
import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import com.iflytek.rpa.auth.core.entity.LoginDto;
import com.iflytek.rpa.auth.sp.uap.dao.UserDao;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.time.LocalDateTime;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * 黑名单 AOP 切面
 * 监控 /login-status 和 /pre-authenticate 接口
 * - /login-status: 其他服务在校验 session 时都会调用该接口
 * - /pre-authenticate: 登录预验证接口，防止被封禁用户登录
 * 如果在黑名单中，立即注销会话并抛出异常
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class BlacklistAspect {

    private final BlackListService blackListService;
    private final UserDao userDao;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    /**
     * 定义切点：拦截 LoginController 的 loginStatus 方法（/login-status 接口）
     */
    @Pointcut("execution(* com.iflytek.rpa.auth.core.controller.LoginController.loginStatus(..))")
    public void loginStatusPointcut() {}

    /**
     * 定义切点：拦截 LoginController 的 preAuthenticate 方法（/pre-authenticate 接口）
     */
    @Pointcut("execution(* com.iflytek.rpa.auth.core.controller.LoginController.preAuthenticate(..))")
    public void preAuthenticatePointcut() {}

    /**
     * 组合切点：loginStatus 或 preAuthenticate
     */
    @Pointcut("loginStatusPointcut() || preAuthenticatePointcut()")
    public void loginCheckPointcut() {}

    /**
     * 环绕通知：在登录相关方法执行前检查黑名单
     */
    @Around("loginCheckPointcut()")
    public Object checkBlacklist(ProceedingJoinPoint joinPoint) throws Throwable {
        try {
            // 获取当前请求
            ServletRequestAttributes attributes =
                    (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes == null) {
                // 非 Web 请求，直接放行
                return joinPoint.proceed();
            }

            HttpServletRequest request = attributes.getRequest();
            HttpServletResponse response = attributes.getResponse();
            String requestURI = request.getRequestURI();

            String userId = null;
            String username = null;

            // 判断是哪个接口
            if (requestURI.contains("/pre-authenticate")) {
                // /pre-authenticate 接口：从请求参数中获取手机号，然后查询用户ID
                Object[] args = joinPoint.getArgs();
                if (args != null && args.length > 0) {
                    // 第一个参数应该是 LoginDto
                    Object firstArg = args[0];
                    if (firstArg instanceof LoginDto) {
                        LoginDto loginDto = (LoginDto) firstArg;
                        String phone = loginDto.getPhone();

                        if (StringUtils.hasText(phone)) {
                            // 通过手机号查询用户ID
                            userId = getUserIdByPhone(phone);
                            username = phone; // 暂时使用手机号作为用户名
                            log.debug("从 pre-authenticate 请求中获取手机号: {}, userId: {}", phone, userId);
                        }
                    }
                }
            } else {
                // /login-status 接口：从 session 中获取已登录用户
                UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
                if (loginUser != null) {
                    userId = loginUser.getId();
                    username = loginUser.getLoginName();
                }
            }

            // 如果获取到用户ID，检查是否在黑名单中
            if (userId != null && !userId.isEmpty()) {
                BlacklistCacheDto blacklist = blackListService.isBlocked(userId);

                if (blacklist != null) {
                    // 用户在黑名单中，拒绝登录
                    log.warn(
                            "AOP 拦截到黑名单用户尝试登录，userId: {}, username: {}, reason: {}",
                            userId,
                            username,
                            blacklist.getReason());

                    // 如果是已登录用户（/login-status），强制注销会话
                    // /pre-authenticate 接口本身还没有登录，无需注销会话
                    if (!requestURI.contains("/pre-authenticate") && response != null) {
                        blackListService.forceLogout(request, response);
                    }

                    // 将时间戳转换为 LocalDateTime
                    LocalDateTime endTime = blacklist.getEndTimeMillis() != null
                            ? LocalDateTime.ofInstant(
                                    java.time.Instant.ofEpochMilli(blacklist.getEndTimeMillis()),
                                    java.time.ZoneId.systemDefault())
                            : null;

                    // 动态计算剩余封禁时间（秒）
                    long remainingSeconds = 0;
                    if (endTime != null) {
                        remainingSeconds = java.time.Duration.between(LocalDateTime.now(), endTime)
                                .getSeconds();
                        if (remainingSeconds < 0) {
                            remainingSeconds = 0;
                        }
                    }

                    // 抛出封禁异常
                    throw new UserBlockedException(
                            blacklist.getUserId(),
                            blacklist.getUsername(),
                            blacklist.getReason(),
                            endTime,
                            remainingSeconds);
                }
            }

            // 继续执行业务方法
            return joinPoint.proceed();

        } catch (UserBlockedException | ShouldBeBlackException e) {
            throw e;
        } catch (Throwable e) {
            log.error("黑名单 AOP 执行异常", e);
            // 其他异常继续执行，避免影响正常业务
            return joinPoint.proceed();
        }
    }

    /**
     * 通过手机号查询用户ID
     */
    private String getUserIdByPhone(String phone) {
        try {
            String userId = userDao.getUserIdByPhone(phone, databaseName);
            if (!StringUtils.hasText(userId)) {
                log.debug("未找到用户，手机号: {}", phone);
                return null;
            }
            return userId;
        } catch (Exception e) {
            log.debug("通过手机号查询用户ID失败: {}", phone, e);
            return null;
        }
    }
}
