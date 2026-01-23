package com.iflytek.rpa.auth.conf;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Map;
import java.util.UUID;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

/**
 * 统一请求日志过滤器，记录请求/响应信息与耗时。
 */
@Slf4j
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
public class RequestLoggingFilter extends OncePerRequestFilter {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();
    private static final int MAX_LOG_LENGTH = 2000;
    private static final String REQUEST_ID_KEY = "requestId";
    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;
    private static final String REQUEST_PREFIX = "REQUEST_LOG";
    private static final String RESPONSE_PREFIX = "RESPONSE_LOG";
    private static final String EXCEPTION_PREFIX = "EXCEPTION_LOG";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        ContentCachingRequestWrapper requestWrapper = wrapRequest(request);
        ContentCachingResponseWrapper responseWrapper = wrapResponse(response);
        String requestId = UUID.randomUUID().toString().replace("-", "");
        MDC.put(REQUEST_ID_KEY, requestId);

        long startTime = System.currentTimeMillis();
        String path = requestWrapper.getRequestURI();
        String method = requestWrapper.getMethod();
        String query = StringUtils.defaultString(requestWrapper.getQueryString(), "");
        String startTimeText = LocalDateTime.now().format(TIME_FORMATTER);
        boolean hasException = false;
        Exception capturedException = null;

        try {
            filterChain.doFilter(requestWrapper, responseWrapper);
        } catch (Exception ex) {
            hasException = true;
            capturedException = ex;
            long duration = System.currentTimeMillis() - startTime;
            log.error(
                    "{} requestId={} method={} path={} duration={}ms error={}",
                    EXCEPTION_PREFIX,
                    requestId,
                    method,
                    path,
                    duration,
                    ex.getMessage(),
                    ex);
            throw ex;
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            String reqBody =
                    shouldLogBody(requestWrapper.getContentType()) ? getRequestBody(requestWrapper) : "[ignored]";
            String respBody =
                    shouldLogBody(responseWrapper.getContentType()) ? getResponseBody(responseWrapper) : "[ignored]";

            log.info(
                    "{} requestId={} time={} method={} path={} query={} params={} reqBody={} duration={}ms hasException={}",
                    REQUEST_PREFIX,
                    requestId,
                    startTimeText,
                    method,
                    path,
                    query,
                    truncate(buildParameterJson(requestWrapper)),
                    truncate(reqBody),
                    duration,
                    hasException);

            log.info(
                    "{} requestId={} method={} path={} status={} duration={}ms respBody={} hasException={} error={}",
                    RESPONSE_PREFIX,
                    requestId,
                    method,
                    path,
                    responseWrapper.getStatus(),
                    duration,
                    truncate(respBody),
                    hasException,
                    capturedException == null ? "" : truncate(capturedException.getMessage()));

            responseWrapper.copyBodyToResponse();
            MDC.remove(REQUEST_ID_KEY);
        }
    }

    private ContentCachingRequestWrapper wrapRequest(HttpServletRequest request) {
        return request instanceof ContentCachingRequestWrapper
                ? (ContentCachingRequestWrapper) request
                : new ContentCachingRequestWrapper(request);
    }

    private ContentCachingResponseWrapper wrapResponse(HttpServletResponse response) {
        return response instanceof ContentCachingResponseWrapper
                ? (ContentCachingResponseWrapper) response
                : new ContentCachingResponseWrapper(response);
    }

    private String buildParameterJson(HttpServletRequest request) {
        try {
            Map<String, String[]> parameterMap = request.getParameterMap();
            if (parameterMap == null || parameterMap.isEmpty()) {
                return "{}";
            }
            return OBJECT_MAPPER.writeValueAsString(parameterMap);
        } catch (JsonProcessingException e) {
            return "[unserializable-params]";
        }
    }

    private String getRequestBody(ContentCachingRequestWrapper requestWrapper) {
        byte[] buf = requestWrapper.getContentAsByteArray();
        if (buf.length == 0) {
            return "";
        }
        return new String(buf, StandardCharsets.UTF_8);
    }

    private String getResponseBody(ContentCachingResponseWrapper responseWrapper) {
        byte[] buf = responseWrapper.getContentAsByteArray();
        if (buf.length == 0) {
            return "";
        }
        return new String(buf, StandardCharsets.UTF_8);
    }

    private String truncate(String source) {
        if (source == null) {
            return "";
        }
        if (source.length() <= MAX_LOG_LENGTH) {
            return source;
        }
        return source.substring(0, MAX_LOG_LENGTH) + "...(truncated)";
    }

    private boolean shouldLogBody(String contentType) {
        if (contentType == null) {
            return true;
        }
        String lower = contentType.toLowerCase();
        return !(lower.contains("multipart/form-data") || lower.contains("octet-stream"));
    }

    @Override
    protected boolean shouldNotFilterAsyncDispatch() {
        return false;
    }

    @Override
    protected boolean shouldNotFilterErrorDispatch() {
        return false;
    }
}
