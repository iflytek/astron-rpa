package com.iflytek.rpa.astronAgent.filter;

import java.io.IOException;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * API Key认证过滤器
 * 用于astronAgent接口的简单API Key认证
 */
@Slf4j
@Component
@Order(org.springframework.core.Ordered.HIGHEST_PRECEDENCE + 10)
public class ApiKeyAuthFilter extends OncePerRequestFilter {

    @Value("${astron.agent.api.key:}")
    private String validApiKey;

    private static final String API_KEY_HEADER = "X-API-Key";
    private static final String ASTRON_AGENT_PATH_PREFIX = "/astron-agent";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String requestPath = request.getRequestURI();

        // 提取路径后缀，移除context-path前缀（如/api/robot）
        String pathSuffix = extractPathSuffix(requestPath);

        // 只对astron-agent路径进行API Key验证（支持带前缀和不带前缀的路径）
        if (pathSuffix != null && pathSuffix.startsWith(ASTRON_AGENT_PATH_PREFIX)) {
            String apiKey = request.getHeader(API_KEY_HEADER);

            // 如果配置了API Key，则进行验证
            if (StringUtils.isNotBlank(validApiKey)) {
                if (StringUtils.isBlank(apiKey) || !validApiKey.equals(apiKey)) {
                    log.warn("API Key验证失败，请求路径: {}", requestPath);
                    response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                    response.setContentType("application/json;charset=UTF-8");
                    response.getWriter().write("{\"code\":401,\"message\":\"API Key验证失败\"}");
                    return;
                }
            }
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 从完整URI中提取路径后缀，移除context-path前缀
     * 例如：/api/robot/astron-agent/copy-robot -> /astron-agent/copy-robot
     * /astron-agent/copy-robot -> /astron-agent/copy-robot
     */
    private String extractPathSuffix(String requestUri) {
        if (StringUtils.isBlank(requestUri)) {
            return null;
        }

        // 移除常见的API前缀
        String[] prefixes = {"/api/robot/", "/api/v1/", "/api/", "/robot/"};
        for (String prefix : prefixes) {
            if (requestUri.startsWith(prefix)) {
                String suffix = requestUri.substring(prefix.length());
                // 确保以/开头
                if (!suffix.startsWith("/")) {
                    suffix = "/" + suffix;
                }
                return suffix;
            }
        }

        // 如果没有匹配到前缀，返回原路径
        return requestUri;
    }
}
