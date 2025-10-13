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
import org.springframework.security.core.context.SecurityContextHolder;
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
    private final String frontendUrl;
    private final String casdoorUrl;

    public SecurityConfig(
            SessionAuthenticationFilter sessionAuthenticationFilter,
            @Value("${casdoor.redirect-url}") String redirectUrl,
            @Value("${casdoor.endpoint}") String casdoorUrl) {
        this.sessionAuthenticationFilter = sessionAuthenticationFilter;
        this.frontendUrl = parseOrigin(redirectUrl);
        this.casdoorUrl = parseOrigin(casdoorUrl);
    }

    private String parseOrigin(String url) {
        int protocol = url.startsWith("https://") ? 5 : 4;
        int slash = url.indexOf('/', protocol + 3);
        return slash == -1 ? url : url.substring(0, slash);
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
                .mvcMatchers("/user/redirect-url", "/user/sign/in", "/user/sign/out")
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
                .addLogoutHandler(new LogoutHandler() {
                    @Override
                    public void logout(
                            HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
                        try {
                            logger.info("Spring Security logout handler called");

                            // 从session获取用户信息并清除Redis中的服务端token
                            User user = (User) request.getSession().getAttribute("user");
                            String userName = user != null ? user.name : "未知用户";

                            if (user != null) {
                                TokenManager.clearTokens(user.name);
                                logger.info("用户 {} 的服务端token已清除", user.name);
                            }

                            // 清除Spring Security上下文
                            SecurityContextHolder.clearContext();

                            logger.info("用户 {} 登出成功", userName);
                        } catch (Exception e) {
                            logger.error("登出处理异常", e);
                        }
                    }
                })
                .logoutSuccessHandler((request, response, authentication) -> {
                    try {
                        // 登出成功后返回JSON响应
                        response.setStatus(HttpServletResponse.SC_OK);
                        response.setContentType("application/json;charset=UTF-8");
                        response.getWriter().write(AppResponse.success("登出成功").toString());
                    } catch (Exception e) {
                        logger.error("登出成功响应写入异常", e);
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
