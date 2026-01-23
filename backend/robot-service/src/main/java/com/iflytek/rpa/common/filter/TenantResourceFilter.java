package com.iflytek.rpa.common.filter;

import com.iflytek.rpa.base.entity.dto.ResourceConfigDto;
import com.iflytek.rpa.base.service.TenantResourceService;
import com.iflytek.rpa.common.feign.RpaAuthFeign;
import com.iflytek.rpa.utils.response.AppResponse;
import java.io.IOException;
import java.util.Map;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * 租户资源配额校验Filter
 * 拦截请求，根据URL匹配资源，进行功能权限和数量限制的校验
 */
@Slf4j
@Component
@Order() // 优先级放最低
public class TenantResourceFilter extends OncePerRequestFilter {

    private static final String QUOTA_ATTRIBUTE_PREFIX = "QUOTA_";
    private static final AntPathMatcher pathMatcher = new AntPathMatcher();

    @Autowired
    private TenantResourceService tenantResourceService;

    @Autowired
    private RpaAuthFeign rpaAuthFeign;

    /**
     * 白名单路径，不需要进行资源校验
     */
    private static final String[] EXCLUDE_PATHS = {
        "/login", "/logout", "/error", "/actuator", "/swagger", "/v2/api-docs", "/favicon.ico"
    };

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) throws ServletException {
        // OPTIONS请求不拦截
        if (HttpMethod.OPTIONS.matches(request.getMethod())) {
            return true;
        }

        String uri = request.getRequestURI();
        // 检查白名单
        for (String excludePath : EXCLUDE_PATHS) {
            if (uri.contains(excludePath)) {
                return true;
            }
        }

        return false;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        try {
            // 获取租户ID
            String tenantId = getTenantId(request);
            if (StringUtils.isBlank(tenantId)) {
                log.debug("无法获取租户ID，跳过资源校验");
                filterChain.doFilter(request, response);
                return;
            }

            // 获取请求URI
            String requestUri = request.getRequestURI();

            // 获取租户资源配置
            Map<String, ResourceConfigDto> resourceConfigMap = tenantResourceService.getTenantResourceConfig(tenantId);
            if (resourceConfigMap.isEmpty()) {
                log.debug("租户资源配置为空，跳过资源校验，tenantId: {}", tenantId);
                filterChain.doFilter(request, response);
                return;
            }

            // 查找匹配的资源
            ResourceConfigDto matchedResource = findMatchingResource(requestUri, resourceConfigMap);
            if (matchedResource == null) {
                // 没有匹配的资源，直接放行
                filterChain.doFilter(request, response);
                return;
            }

            // 获取资源代码
            String resourceCode = getResourceCodeByConfig(matchedResource, resourceConfigMap);
            if (StringUtils.isBlank(resourceCode)) {
                log.warn("无法获取资源代码，跳过资源校验");
                filterChain.doFilter(request, response);
                return;
            }

            // 层级校验：检查父级资源是否有效
            if (!checkParentResource(resourceCode, matchedResource, resourceConfigMap)) {
                log.warn("父级资源无效，拒绝访问，tenantId: {}, resourceCode: {}", tenantId, resourceCode);
                sendForbiddenResponse(response, "父级资源未启用");
                return;
            }

            // 权限校验
            String resourceType = matchedResource.getType();
            if ("SWITCH".equals(resourceType)) {
                // 开关类型：final为0则返回403
                Integer finalValue = matchedResource.getFinalValue();
                if (finalValue == null || finalValue == 0) {
                    log.warn("资源开关已关闭，拒绝访问，tenantId: {}, resourceCode: {}", tenantId, resourceCode);
                    sendForbiddenResponse(response, "该功能未启用");
                    return;
                }
            }
            //            else if ("QUOTA".equals(resourceType)) {
            //                // 配额类型：将final限制值存入request属性，供后续业务层使用
            //                Integer finalValue = matchedResource.getFinalValue();
            //                if (finalValue != null) {
            //                    String attributeName = QUOTA_ATTRIBUTE_PREFIX + resourceCode;
            //                    request.setAttribute(attributeName, finalValue);
            //                    log.debug("设置配额限制，tenantId: {}, resourceCode: {}, quota: {}", tenantId, resourceCode,
            // finalValue);
            //                }
            //            }

            // 校验通过，继续执行
            filterChain.doFilter(request, response);

        } catch (Exception e) {
            log.error("资源校验过程中发生异常", e);
            // 发生异常时，为了不影响系统正常运行，可以选择放行或返回错误
            // 这里选择放行，但记录错误日志
            filterChain.doFilter(request, response);
        }
    }

    /**
     * 获取租户ID
     */
    private String getTenantId(HttpServletRequest request) {
        try {
            // 尝试从认证服务获取租户ID
            AppResponse<String> response = rpaAuthFeign.getTenantId();
            if (response != null && response.ok() && response.getData() != null) {
                return response.getData();
            }
        } catch (Exception e) {
            log.debug("从认证服务获取租户ID失败", e);
        }

        // 如果从认证服务获取失败，可以尝试从header或session中获取
        String tenantId = request.getHeader("tenantId");
        if (StringUtils.isNotBlank(tenantId)) {
            return tenantId;
        }

        return null;
    }

    /**
     * 查找匹配的资源
     * 支持多种匹配方式：
     * 1. 直接匹配完整路径
     * 2. 匹配路径后缀（去除/api/robot等前缀）
     * 3. 支持AntPathMatcher通配符
     */
    private ResourceConfigDto findMatchingResource(
            String requestUri, Map<String, ResourceConfigDto> resourceConfigMap) {
        for (Map.Entry<String, ResourceConfigDto> entry : resourceConfigMap.entrySet()) {
            ResourceConfigDto config = entry.getValue();
            if (config.getUrls() != null && !config.getUrls().isEmpty()) {
                for (String urlPattern : config.getUrls()) {
                    // 1. 直接匹配完整路径
                    if (pathMatcher.match(urlPattern, requestUri)) {
                        log.debug(
                                "匹配到资源（完整路径），requestUri: {}, urlPattern: {}, resourceCode: {}",
                                requestUri,
                                urlPattern,
                                entry.getKey());
                        return config;
                    }

                    // 2. 如果urlPattern不以/开头，尝试匹配路径后缀
                    if (!urlPattern.startsWith("/")) {
                        // 从requestUri中提取路径部分进行匹配
                        String normalizedPattern = "/" + urlPattern;
                        if (pathMatcher.match(normalizedPattern, requestUri)) {
                            log.debug(
                                    "匹配到资源（规范化路径），requestUri: {}, urlPattern: {}, resourceCode: {}",
                                    requestUri,
                                    normalizedPattern,
                                    entry.getKey());
                            return config;
                        }
                    }

                    // 3. 尝试从requestUri中提取路径后缀进行匹配
                    // 例如：/api/robot/market-invite/generate-invite-link -> /market-invite/generate-invite-link
                    String pathSuffix = extractPathSuffix(requestUri);
                    if (pathSuffix != null) {
                        // 匹配完整路径模式
                        if (pathMatcher.match(urlPattern, pathSuffix)) {
                            log.debug(
                                    "匹配到资源（路径后缀），requestUri: {}, pathSuffix: {}, urlPattern: {}, resourceCode: {}",
                                    requestUri,
                                    pathSuffix,
                                    urlPattern,
                                    entry.getKey());
                            return config;
                        }
                        // 如果urlPattern不以/开头，也尝试匹配
                        if (!urlPattern.startsWith("/")) {
                            String normalizedPattern = "/" + urlPattern;
                            if (pathMatcher.match(normalizedPattern, pathSuffix)) {
                                log.debug(
                                        "匹配到资源（路径后缀规范化），requestUri: {}, pathSuffix: {}, urlPattern: {}, resourceCode: {}",
                                        requestUri,
                                        pathSuffix,
                                        normalizedPattern,
                                        entry.getKey());
                                return config;
                            }
                        }
                    }

                    // 4. 支持包含匹配（如果urlPattern是路径的一部分）
                    if (requestUri.contains(urlPattern) || requestUri.endsWith(urlPattern)) {
                        log.debug(
                                "匹配到资源（包含匹配），requestUri: {}, urlPattern: {}, resourceCode: {}",
                                requestUri,
                                urlPattern,
                                entry.getKey());
                        return config;
                    }
                }
            }
        }
        return null;
    }

    /**
     * 从完整URI中提取路径后缀
     * 例如：/api/robot/market-invite/generate-invite-link -> /market-invite/generate-invite-link
     * /api/v1/design/create -> /design/create
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

    /**
     * 根据配置获取资源代码
     */
    private String getResourceCodeByConfig(ResourceConfigDto config, Map<String, ResourceConfigDto> resourceConfigMap) {
        for (Map.Entry<String, ResourceConfigDto> entry : resourceConfigMap.entrySet()) {
            if (entry.getValue() == config) {
                return entry.getKey();
            }
        }
        return null;
    }

    /**
     * 检查父级资源是否有效
     * 如果资源有父级，则检查父级资源的final值（对于SWITCH类型，final必须为1）
     */
    private boolean checkParentResource(
            String resourceCode, ResourceConfigDto resourceConfig, Map<String, ResourceConfigDto> resourceConfigMap) {
        String parentCode = resourceConfig.getParent();
        if (StringUtils.isBlank(parentCode)) {
            // 没有父级，直接返回true
            return true;
        }

        ResourceConfigDto parentConfig = resourceConfigMap.get(parentCode);
        if (parentConfig == null) {
            log.warn("父级资源配置不存在，parentCode: {}", parentCode);
            return false;
        }

        // 递归检查父级的父级
        if (!checkParentResource(parentCode, parentConfig, resourceConfigMap)) {
            return false;
        }

        // 检查父级资源的final值
        Integer parentFinalValue = parentConfig.getFinalValue();
        String parentType = parentConfig.getType();

        if ("SWITCH".equals(parentType)) {
            // 对于SWITCH类型，final必须为1才有效
            return parentFinalValue != null && parentFinalValue == 1;
        } else if ("QUOTA".equals(parentType)) {
            // 对于QUOTA类型，final必须大于0才有效
            return parentFinalValue != null && parentFinalValue > 0;
        }

        return true;
    }

    /**
     * 发送403 Forbidden响应
     */
    private void sendForbiddenResponse(HttpServletResponse response, String message) throws IOException {
        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.setContentType("application/json;charset=UTF-8");
        String jsonResponse = String.format("{\"code\":\"403\",\"message\":\"%s\",\"data\":null}", message);
        response.getWriter().write(jsonResponse);
        response.getWriter().flush();
    }
}
