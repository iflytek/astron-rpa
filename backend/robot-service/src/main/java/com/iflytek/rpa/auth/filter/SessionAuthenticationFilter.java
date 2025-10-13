package com.iflytek.rpa.auth.filter;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import java.io.IOException;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.casbin.casdoor.entity.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * @desc: Session认证过滤器 - 基于session的OAuth2.0+OIDC认证
 * @author: AI Assistant
 * @create: 2025/10/11
 */
@Component
public class SessionAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger logger = LoggerFactory.getLogger(SessionAuthenticationFilter.class);

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {

        // 检查是否已经认证
        if (SecurityContextHolder.getContext().getAuthentication() != null) {
            chain.doFilter(request, response);
            return;
        }

        // 从session中获取用户信息
        HttpSession session = request.getSession(false);
        if (session == null) {
            chain.doFilter(request, response);
            return;
        }

        User user = (User) session.getAttribute("user");
        if (user == null) {
            chain.doFilter(request, response);
            return;
        }

        // 创建Spring Security认证对象
        try {
            CustomUserDetails userDetails = new CustomUserDetails(user);
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                    userDetails, null, AuthorityUtils.createAuthorityList("ROLE_USER"));

            authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authentication);

            logger.debug("用户 {} 通过session认证成功", user.name);
        } catch (Exception exception) {
            logger.error("session认证失败", exception);
        }

        chain.doFilter(request, response);
    }
}
