package com.iflytek.rpa.auth.utils;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Set;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

/**
 * 菜单权限验证工具类
 * 用于验证用户是否有权限访问指定的菜单路径
 */
@Slf4j
public class MenuPermissionValidator {

    /**
     * 校验菜单权限（仅针对admin平台）
     * @param request HTTP请求
     * @return 验证结果
     */
    public static AppResponse<Boolean> checkMenuPermission(HttpServletRequest request) {
        try {
            // 1. 获取Referer头
            String referer = request.getHeader("Referer");
            if (StringUtils.isNotBlank(referer)) {
                // 2. 从referer解析菜单路径
                String menuPath = extractMenuPathFromReferer(referer);
                if (StringUtils.isNotBlank(menuPath)) {
                    // 3. 从Session获取用户菜单路径列表
                    HttpSession session = request.getSession(false);
                    if (session != null) {
                        @SuppressWarnings("unchecked")
                        Set<String> userMenuPaths = (Set<String>) session.getAttribute("userMenuPaths");
                        if (userMenuPaths != null && !userMenuPaths.isEmpty()) {
                            // 4. 验证菜单路径是否在用户菜单列表中
                            if (!isPathAllowed(menuPath, userMenuPaths)) {
                                log.warn("用户无权限访问菜单路径: {}，Referer: {}", menuPath, referer);
                                return AppResponse.error(ErrorCodeEnum.E_NO_POWER, "未授权：请联系管理员");
                            }
                        } else {
                            log.warn("Session中不存在用户菜单路径列表，无法验证菜单权限，Referer: {}", referer);
                            return AppResponse.error(ErrorCodeEnum.E_NO_POWER, "未授权：菜单权限信息不存在");
                        }
                    } else {
                        log.warn("Session不存在，无法验证菜单权限，Referer: {}", referer);
                        return AppResponse.error(ErrorCodeEnum.E_NO_POWER, "未授权：Session不存在");
                    }
                }
                // 如果无法解析菜单路径，记录日志但放行（可能是API调用等）
            }
            // 如果没有Referer或无法解析，放行（可能是直接访问或API调用）
            return AppResponse.success(true);
        } catch (Exception e) {
            log.error("校验菜单权限失败", e);
            // 校验失败时放行，避免影响正常流程
            return AppResponse.success(true);
        }
    }

    /**
     * 从referer中提取菜单路径
     *
     * @param referer Referer头内容
     * @return 菜单路径，如果解析失败返回null
     */
    public static String extractMenuPathFromReferer(String referer) {
        try {
            URI uri = new URI(referer);
            String path = uri.getPath();

            if (StringUtils.isBlank(path)) {
                return null;
            }

            // 去除/admin前缀（如果存在）
            if (path.startsWith("/admin")) {
                path = path.substring("/admin".length());
            }

            // 如果路径为空或只有斜杠，返回null
            if (StringUtils.isBlank(path) || "/".equals(path)) {
                return null;
            }

            // 去除尾部斜杠
            if (path.endsWith("/") && path.length() > 1) {
                path = path.substring(0, path.length() - 1);
            }

            return path;
        } catch (URISyntaxException e) {
            log.debug("解析Referer URI失败: {}", referer, e);
            return null;
        }
    }

    /**
     * 检查路径是否在允许的菜单路径列表中
     * 支持精确匹配和前缀匹配
     *
     * @param path 要检查的路径
     * @param allowedPaths 允许的菜单路径集合
     * @return 如果允许返回true，否则返回false
     */
    public static boolean isPathAllowed(String path, Set<String> allowedPaths) {
        if (StringUtils.isBlank(path) || allowedPaths == null || allowedPaths.isEmpty()) {
            return false;
        }

        // 标准化路径
        path = normalizeMenuPath(path);

        // 精确匹配
        if (allowedPaths.contains(path)) {
            return true;
        }

        // 前缀匹配：检查是否有父级菜单路径
        // 例如：用户有/schedule，则/schedule/task也允许
        for (String allowedPath : allowedPaths) {
            String normalizedAllowedPath = normalizeMenuPath(allowedPath);
            if (StringUtils.isNotBlank(normalizedAllowedPath) && path.startsWith(normalizedAllowedPath + "/")) {
                return true;
            }
        }

        return false;
    }

    /**
     * 标准化菜单路径
     * @param path 原始路径
     * @return 标准化后的路径
     */
    public static String normalizeMenuPath(String path) {
        if (StringUtils.isBlank(path)) {
            return path;
        }
        path = path.trim();
        // 去除尾部斜杠
        if (path.endsWith("/") && path.length() > 1) {
            path = path.substring(0, path.length() - 1);
        }
        return path;
    }
}
