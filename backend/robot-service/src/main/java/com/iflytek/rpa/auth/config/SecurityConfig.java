package com.iflytek.rpa.auth.config;

import com.iflytek.rpa.auth.filter.SessionAuthenticationFilter;
import com.iflytek.rpa.auth.utils.ResponseUtils;
import com.iflytek.rpa.auth.utils.TokenManager;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.Collections;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.casbin.casdoor.entity.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.logout.LogoutHandler;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * @desc: 安全相关配置
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/15 15:23
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    private static final Logger logger = LoggerFactory.getLogger(SecurityConfig.class);

    private final SessionAuthenticationFilter sessionAuthenticationFilter;

    @Value("${casdoor.external-endpoint}")
    private String externalEndPoint;

    @Value("${casdoor.application-name}")
    private String applicationName;

    @Value("${casdoor.redirect-url}")
    private String frontendUrl;

    public SecurityConfig(SessionAuthenticationFilter sessionAuthenticationFilter) {
        this.sessionAuthenticationFilter = sessionAuthenticationFilter;
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // enable CORS and disable CSRF
        http = http.cors(corsConfig -> corsConfig.configurationSource(configurationSource()))
                .csrf()
                .disable();

        // 启用session管理（OAuth2.0+OIDC标准流程使用session）
        http.sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1) // 限制同一用户的并发session数
                .maxSessionsPreventsLogin(false) // 新登录踢掉旧session
                .and();

        // 配置访问权限
        http.authorizeRequests(authorize -> authorize
                // 公开端点：OAuth2.0授权相关
                .mvcMatchers("/user/redirect-url", "/user/sign/in", "/user/sign/out", "/example/insert")
                .permitAll()
                // 需要认证的端点
                .mvcMatchers("/user/api/**", "/api/**")
                .authenticated()
                // 其他所有请求都需要认证
                .anyRequest()
                .authenticated());

        // set unauthorized requests exception handler
        http = http.exceptionHandling()
                .authenticationEntryPoint((request, response, ex) -> ResponseUtils.fail(response, "unauthorized"))
                .and();

        // 配置登出处理（OAuth2.0+OIDC标准流程）
        http.logout(logoutConfig -> logoutConfig
                .logoutUrl("/user/sign/out")
                // Spring Security自动清除SecurityContext和使session失效
                .invalidateHttpSession(true)
                .clearAuthentication(true)
                .addLogoutHandler(new LogoutHandler() {
                    @Override
                    public void logout(
                            HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
                        // 只处理业务层面的清理工作，不干涉Spring Security的标准流程
                        try {
                            logger.info("执行自定义登出处理");

                            // 从session获取用户信息（在session失效前）
                            User user = (User) request.getSession().getAttribute("user");
                            if (user != null) {
                                // 获取accessToken并存储到request attribute供SuccessHandler使用
                                String accessToken = TokenManager.getAccessToken(user.name);
                                request.setAttribute("logout_access_token", accessToken);
                                request.setAttribute("logout_user_name", user.name);

                                // 清除Redis中的token
                                TokenManager.clearTokens(user.name);
                                logger.info("用户 {} 的Redis token已清除", user.name);
                            } else {
                                logger.warn("session中未找到用户信息，可能已过期");
                            }
                        } catch (Exception e) {
                            logger.error("自定义登出处理异常", e);
                        }
                    }
                })
                .logoutSuccessHandler((request, response, authentication) -> {
                    try {
                        // 从request attribute获取之前保存的accessToken
                        String accessToken = (String) request.getAttribute("logout_access_token");
                        String userName = (String) request.getAttribute("logout_user_name");

                        logger.info("用户 {} 登出成功", userName != null ? userName : "未知");

                        // 构造Casdoor的登出URL（OIDC RP-Initiated Logout）
                        String casdoorLogoutUrl = String.format(
                                externalEndPoint + "/api/logout?post_logout_redirect_uri=%s&id_token_hint=%s&state=%s",
                                java.net.URLEncoder.encode(frontendUrl, "UTF-8"),
                                accessToken != null ? accessToken : "",
                                applicationName);

                        logger.info("返回Casdoor登出URL给前端: {}", casdoorLogoutUrl);

                        // 返回JSON响应，包含Casdoor登出URL
                        response.setStatus(HttpServletResponse.SC_OK);
                        response.setContentType("application/json;charset=UTF-8");

                        String jsonResponse = String.format(
                                "{\"code\":200,\"message\":\"登出成功\",\"data\":{\"logoutUrl\":\"%s\"}}",
                                casdoorLogoutUrl);
                        response.getWriter().write(jsonResponse);
                    } catch (Exception e) {
                        logger.error("登出响应写入异常", e);
                        // 异常时返回基础成功响应
                        try {
                            response.setStatus(HttpServletResponse.SC_OK);
                            response.setContentType("application/json;charset=UTF-8");
                            response.getWriter()
                                    .write(AppResponse.success("登出成功").toString());
                        } catch (Exception ex) {
                            logger.error("登出异常响应写入失败", ex);
                        }
                    }
                }));

        // 添加session认证过滤器
        http.addFilterBefore(
                sessionAuthenticationFilter, org.springframework.security.web.authentication.logout.LogoutFilter.class);
    }

    @Bean
    CorsConfigurationSource configurationSource() {
        CorsConfiguration corsConfiguration = new CorsConfiguration();
        corsConfiguration.setAllowCredentials(true);
        corsConfiguration.setAllowedHeaders(Collections.singletonList("*"));
        corsConfiguration.setAllowedMethods(Collections.singletonList("*"));
        corsConfiguration.setAllowedOrigins(Collections.singletonList("*"));
        corsConfiguration.setMaxAge(3600L);
        corsConfiguration.setExposedHeaders(Collections.singletonList("*"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfiguration);

        return source;
    }
}
