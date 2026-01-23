package com.iflytek.rpa.common.filter;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.*;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.util.StreamUtils;
import org.springframework.web.client.DefaultResponseErrorHandler;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * 通过调用认证服务的 session 校验接口，复用 UAP 的认证结果。
 * session 有效直接放行，无效时将认证服务的响应原样返回给前端。
 */
@Slf4j
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 5)
public class SessionValidationFilter extends OncePerRequestFilter {

    /**
     * 认证服务基础地址
     */
    @Value("${auth.base-url:http://localhost:10251}")
    private String authBaseUrl;

    /**
     * 校验 session 的路径，默认 /api/rpa-auth/check-session
     */
    @Value("${auth.check-session-path:/api/rpa-auth/check-session}")
    private String checkSessionPath;

    /**
     * 拼装后的完整校验地址
     */
    private String checkSessionUrl;

    /**
     * 和 UAP 保持一致的白名单，命中则不校验 session。
     */
    @Value("${uap.session-filter-exclude:}")
    private String sessionFilterExclude;

    private final RestTemplate restTemplate;

    public SessionValidationFilter(RestTemplateBuilder restTemplateBuilder) {
        // 禁止跟随 302，方便把 auth 的原始响应返回给前端
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory() {
            @Override
            protected void prepareConnection(HttpURLConnection connection, String httpMethod) throws IOException {
                super.prepareConnection(connection, httpMethod);
                connection.setInstanceFollowRedirects(false);
            }
        };
        requestFactory.setConnectTimeout(3000);
        requestFactory.setReadTimeout(3000);

        this.restTemplate = restTemplateBuilder
                .requestFactory(() -> requestFactory)
                // 不抛出异常，保留状态码给调用方处理
                .errorHandler(new DefaultResponseErrorHandler() {
                    @Override
                    public boolean hasError(ClientHttpResponse response) throws IOException {
                        return false;
                    }
                })
                .build();
    }

    @javax.annotation.PostConstruct
    public void initCheckSessionUrl() {
        String base = StringUtils.removeEnd(authBaseUrl, "/");
        String path = StringUtils.prependIfMissing(checkSessionPath, "/");
        this.checkSessionUrl = base + path;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
        if (HttpMethod.OPTIONS.matches(request.getMethod())) {
            return true;
        }
        String uri = request.getRequestURI();

        // astron-agent接口使用API Key认证，不需要session校验
        if (uri.contains("/astron-agent")) {
            return true;
        }

        if (StringUtils.isBlank(sessionFilterExclude)) {
            return false;
        }
        List<String> excludeList = Arrays.stream(sessionFilterExclude.split(","))
                .map(String::trim)
                .filter(StringUtils::isNotBlank)
                .collect(Collectors.toList());
        return excludeList.stream().anyMatch(uri::contains);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        HttpHeaders headers = new HttpHeaders();
        copyForwardHeaders(request, headers);
        HttpEntity<Void> entity = new HttpEntity<>(headers);

        ResponseEntity<byte[]> authResponse;
        try {
            authResponse = restTemplate.exchange(checkSessionUrl, HttpMethod.GET, entity, byte[].class);
        } catch (Exception ex) {
            log.error("调用认证服务校验 session 失败", ex);
            response.sendError(HttpStatus.INTERNAL_SERVER_ERROR.value(), "session check failed");
            return;
        }

        HttpStatus status = authResponse.getStatusCode();
        byte[] body = authResponse.getBody();

        // 如果状态码是2xx，需要检查响应体是否是重定向JSON或空间到期响应
        if (status.is2xxSuccessful()) {
            // 检查是否是包含 ret:302 的重定向JSON响应
            if (isRedirectJsonResponse(body)) {
                // 原样返回重定向JSON
                writeBackResponse(response, status.value(), authResponse.getHeaders(), body);
                return;
            }
            // 检查是否是空间到期响应
            if (isSpaceExpiredResponse(body)) {
                // 原样返回空间到期响应，前端会处理退出登录
                writeBackResponse(response, status.value(), authResponse.getHeaders(), body);
                return;
            }
            // 检查是否是单点登录失效响应（账号在其他地方登录）
            if (isSingleSignOnInvalidResponse(body)) {
                // 原样返回单点登录失效响应，前端会处理退出登录
                writeBackResponse(response, status.value(), authResponse.getHeaders(), body);
                return;
            }
            // 正常响应，放行
            filterChain.doFilter(request, response);
            return;
        }

        // 非2xx状态码，原样返回
        writeBackResponse(response, status.value(), authResponse.getHeaders(), body);
    }

    private void copyForwardHeaders(HttpServletRequest request, HttpHeaders headers) {
        // 复制 Cookie，用于复用 session
        String cookieHeader = request.getHeader(HttpHeaders.COOKIE);
        if (StringUtils.isNotBlank(cookieHeader)) {
            headers.add(HttpHeaders.COOKIE, cookieHeader);
        } else {
            Cookie[] cookies = request.getCookies();
            if (cookies != null && cookies.length > 0) {
                String cookieString = Arrays.stream(cookies)
                        .map(cookie -> cookie.getName() + "=" + cookie.getValue())
                        .collect(Collectors.joining("; "));
                if (StringUtils.isNotBlank(cookieString)) {
                    headers.add(HttpHeaders.COOKIE, cookieString);
                }
            }
        }

        // 传递可能参与认证的 header
        copyHeaderIfPresent(request, headers, "Authorization");
        copyHeaderIfPresent(request, headers, "X-User-Id");

        // 添加 x-requested-with header，标识为 AJAX 请求
        headers.add("x-requested-with", "XMLHttpRequest");
    }

    private void copyHeaderIfPresent(HttpServletRequest request, HttpHeaders headers, String name) {
        String value = request.getHeader(name);
        if (StringUtils.isNotBlank(value)) {
            headers.add(name, value);
        }
    }

    /**
     * 检查响应体是否是包含 ret:302 的重定向JSON响应
     * @param body 响应体字节数组
     * @return 如果是重定向JSON返回true，否则返回false
     */
    private boolean isRedirectJsonResponse(byte[] body) {
        if (body == null || body.length == 0) {
            return false;
        }
        try {
            String bodyStr = new String(body, java.nio.charset.StandardCharsets.UTF_8).trim();
            // 检查是否包含 "ret":302 或 "ret": 302（带空格）
            return bodyStr.contains("\"ret\":302") || bodyStr.contains("\"ret\": 302");
        } catch (Exception e) {
            log.debug("解析响应体失败，不视为重定向JSON", e);
            return false;
        }
    }

    /**
     * 检查响应体是否是空间到期响应
     * @param body 响应体字节数组
     * @return 如果是空间到期响应返回true，否则返回false
     */
    private boolean isSpaceExpiredResponse(byte[] body) {
        if (body == null || body.length == 0) {
            return false;
        }
        try {
            String bodyStr = new String(body, java.nio.charset.StandardCharsets.UTF_8).trim();
            // 只判断错误码900005，接口返回的错误码格式为 "code":"900005"
            return bodyStr.contains("\"code\":\"900005\"");
        } catch (Exception e) {
            log.debug("解析响应体失败，不视为空间到期响应", e);
            return false;
        }
    }

    /**
     * 检查响应体是否是单点登录失效响应（账号在其他地方登录）
     * @param body 响应体字节数组
     * @return 如果是单点登录失效响应返回true，否则返回false
     */
    private boolean isSingleSignOnInvalidResponse(byte[] body) {
        if (body == null || body.length == 0) {
            return false;
        }
        try {
            String bodyStr = new String(body, java.nio.charset.StandardCharsets.UTF_8).trim();
            // 判断错误码900001（E_NOT_LOGIN），并且包含"其他地方登录"的提示
            return bodyStr.contains("\"code\":\"900001\"") && (bodyStr.contains("其他地方登录") || bodyStr.contains("会话已失效"));
        } catch (Exception e) {
            log.debug("解析响应体失败，不视为单点登录失效响应", e);
            return false;
        }
    }

    private void writeBackResponse(HttpServletResponse response, int status, HttpHeaders headers, byte[] body)
            throws IOException {
        response.setStatus(status);
        if (headers != null) {
            headers.forEach((name, values) -> {
                if (HttpHeaders.TRANSFER_ENCODING.equalsIgnoreCase(name)
                        || HttpHeaders.CONTENT_LENGTH.equalsIgnoreCase(name)) {
                    return;
                }
                for (String value : values) {
                    response.addHeader(name, value);
                }
            });
        }
        if (body != null && body.length > 0) {
            StreamUtils.copy(body, response.getOutputStream());
        }
    }
}
