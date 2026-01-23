package com.iflytek.rpa.conf;

import static com.iflytek.rpa.conf.ApiContext.*;

import feign.RequestInterceptor;
import feign.RequestTemplate;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

@Configuration
public class FeignConfiguration implements RequestInterceptor {

    private Logger logger = LoggerFactory.getLogger(getClass());

    @Override
    public void apply(RequestTemplate template) {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes != null) {
            HttpServletRequest request = attributes.getRequest();

            // 传递已有的业务 header
            template.header(CURRENT_USER_ID_KEY, request.getHeader(CURRENT_USER_ID_KEY));
            template.header(CURRENT_TENANT_ID_KEY, request.getHeader(CURRENT_TENANT_ID_KEY));
            template.header(CURRENT_TERMINAL_MAC_KEY, request.getHeader(CURRENT_TERMINAL_MAC_KEY));
            template.header(CURRENT_TERMINAL_NAME_KEY, request.getHeader(CURRENT_TERMINAL_NAME_KEY));

            // 传递认证相关的 header
            String ssoSessionId = request.getHeader("ssoSessionId");
            if (ssoSessionId != null) {
                template.header("ssoSessionId", ssoSessionId);
            }

            String globalToken = request.getHeader("global-token");
            if (globalToken != null) {
                template.header("global-token", globalToken);
            }

            String accountId = request.getHeader("account_id");
            if (accountId != null) {
                template.header("account_id", accountId);
            }

            String authorization = request.getHeader("Authorization");
            if (authorization != null) {
                template.header("Authorization", authorization);
            }

            String xUserId = request.getHeader("X-User-Id");
            if (xUserId != null) {
                template.header("X-User-Id", xUserId);
            }

            String terminalType = request.getHeader("terminalType");
            if (terminalType != null) {
                template.header("terminalType", terminalType);
            }

            String appId = request.getHeader("appId");
            if (appId != null) {
                template.header("appId", appId);
            }

            String ipAddress = request.getHeader("ip-address");
            if (ipAddress != null) {
                template.header("ip-address", ipAddress);
            }

            // 传递 Cookie（重要：用于 Session 认证）
            // 优先使用原始 Cookie header，如果不存在则从 cookies 数组构建
            String cookieHeader = request.getHeader("Cookie");
            if (cookieHeader != null && cookieHeader.trim().length() > 0) {
                template.header("Cookie", cookieHeader);
            } else {
                // 如果原始 Cookie header 不存在，从 cookies 数组构建
                Cookie[] cookies = request.getCookies();
                if (cookies != null && cookies.length > 0) {
                    StringBuilder cookieBuilder = new StringBuilder();
                    for (Cookie cookie : cookies) {
                        if (cookieBuilder.length() > 0) {
                            cookieBuilder.append("; ");
                        }
                        cookieBuilder.append(cookie.getName()).append("=").append(cookie.getValue());
                    }
                    template.header("Cookie", cookieBuilder.toString());
                }
            }
        }
    }
}
