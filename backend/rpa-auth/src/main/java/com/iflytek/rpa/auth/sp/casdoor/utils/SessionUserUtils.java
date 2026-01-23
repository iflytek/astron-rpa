package com.iflytek.rpa.auth.sp.casdoor.utils;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.casbin.casdoor.entity.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * @desc: Session用户工具类，用于从session中获取用户信息
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11
 */
public class SessionUserUtils {

    private static final Logger logger = LoggerFactory.getLogger(SessionUserUtils.class);

    /**
     * 从session中获取Casdoor用户对象
     *
     * @param request HTTP请求
     * @return Casdoor用户对象，如果未登录或session不存在则返回null
     */
    public static User getUserFromSession(HttpServletRequest request) {
        if (request == null) {
            return null;
        }

        try {
            HttpSession session = request.getSession(false);
            if (session == null) {
                return null;
            }

            User user = (User) session.getAttribute("user");
            if (user == null) {
                return null;
            }

            return user;
        } catch (Exception e) {
            logger.warn("从session获取用户信息失败", e);
            return null;
        }
    }

    /**
     * 从session中获取当前租户ID（owner）
     *
     * @param request HTTP请求
     * @return 租户ID（owner），如果未登录或session不存在则返回null
     */
    public static String getTenantOwnerFromSession(HttpServletRequest request) {
        User user = getUserFromSession(request);
        if (user == null) {
            return null;
        }

        if (user.owner != null && !user.owner.isEmpty()) {
            return user.owner;
        }

        return null;
    }

    /**
     * 检查用户是否已登录
     *
     * @param request HTTP请求
     * @return 如果用户已登录返回true，否则返回false
     */
    public static boolean isUserLoggedIn(HttpServletRequest request) {
        User user = getUserFromSession(request);
        return user != null && user.name != null && !user.name.isEmpty();
    }
}
