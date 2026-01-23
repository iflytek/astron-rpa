package com.iflytek.rpa.auth.blacklist.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.blacklist.dto.BlacklistCacheDto;
import com.iflytek.rpa.auth.blacklist.exception.UserBlockedException;
import com.iflytek.rpa.auth.blacklist.service.BlackListService;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import java.io.IOException;
import java.io.PrintWriter;
import java.time.LocalDateTime;
import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.annotation.Order;
// import org.springframework.stereotype.Component; // 已禁用，不再使用

/**
 * 黑名单拦截过滤器
 * 已禁用：与 BlacklistAspect 功能重复
 * 黑名单检查统一由 BlacklistAspect 在 /login-status 接口处理
 *
 * @author system
 * @date 2025-12-16
 */
@Slf4j
// @Component  // 已禁用，不再使用
@Order(2)
@RequiredArgsConstructor
public class BlacklistFilter implements Filter {

    private final BlackListService blackListService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 不需要拦截的路径
     */
    private static final String[] EXCLUDE_PATHS = {
        "/login",
        "/logout",
        "/pre-authenticate",
        "/tenant/list",
        "/verification-code/send",
        "/register",
        "/password/set",
        "/user/exist",
        "/refresh-token",
        "/static/",
        "/public/",
        "/error",
        "/favicon.ico"
    };

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        String requestURI = httpRequest.getRequestURI();

        // 检查是否是不需要拦截的路径
        if (isExcludePath(requestURI)) {
            chain.doFilter(request, response);
            return;
        }

        try {
            // 获取当前登录用户
            UapUser loginUser = UapUserInfoAPI.getLoginUser(httpRequest);

            if (loginUser != null) {
                String userId = loginUser.getId();

                // 检查用户是否在黑名单中
                BlacklistCacheDto blacklist = blackListService.isBlocked(userId);

                if (blacklist != null) {
                    // 用户在黑名单中，拒绝请求
                    log.warn(
                            "黑名单用户尝试访问系统，userId: {}, username: {}, reason: {}",
                            userId,
                            loginUser.getLoginName(),
                            blacklist.getReason());

                    // 强制注销（Filter 已禁用，此代码不会执行）
                    // 注意：Filter 已禁用，注销逻辑由 BlacklistAspect 处理
                    // blackListService.forceLogout(httpRequest, httpResponse);

                    // 返回错误响应
                    sendBlockedResponse(httpResponse, blacklist);
                    return;
                }
            }

            // 继续处理请求
            chain.doFilter(request, response);

        } catch (Exception e) {
            log.error("黑名单过滤器异常", e);
            // 异常时放行，避免影响正常业务
            chain.doFilter(request, response);
        }
    }

    /**
     * 检查是否是排除路径
     */
    private boolean isExcludePath(String requestURI) {
        for (String path : EXCLUDE_PATHS) {
            if (requestURI.contains(path)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 发送封禁响应
     */
    private void sendBlockedResponse(HttpServletResponse response, BlacklistCacheDto blacklist) throws IOException {
        response.setStatus(HttpServletResponse.SC_FORBIDDEN);
        response.setContentType("application/json;charset=UTF-8");

        // 将时间戳转换为 LocalDateTime
        LocalDateTime endTime = blacklist.getEndTimeMillis() != null
                ? LocalDateTime.ofInstant(
                        java.time.Instant.ofEpochMilli(blacklist.getEndTimeMillis()), java.time.ZoneId.systemDefault())
                : null;

        UserBlockedException exception = new UserBlockedException(
                blacklist.getUserId(),
                blacklist.getUsername(),
                blacklist.getReason(),
                endTime,
                blacklist.getRemainingSeconds());

        AppResponse<Object> errorResponse = AppResponse.error(ErrorCodeEnum.E_NO_POWER, exception.getMessage());

        PrintWriter writer = response.getWriter();
        writer.write(objectMapper.writeValueAsString(errorResponse));
        writer.flush();
    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        log.info("黑名单过滤器初始化");
    }

    @Override
    public void destroy() {
        log.info("黑名单过滤器销毁");
    }
}
