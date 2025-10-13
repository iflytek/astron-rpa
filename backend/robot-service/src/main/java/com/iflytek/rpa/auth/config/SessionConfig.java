package com.iflytek.rpa.auth.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.session.data.redis.config.annotation.web.http.EnableRedisHttpSession;
import org.springframework.session.web.http.CookieSerializer;
import org.springframework.session.web.http.DefaultCookieSerializer;

/**
 * @desc: Spring Session配置 - 自动将session存储到Redis并管理Cookie
 * @author: AI Assistant
 * @create: 2025/10/11
 */
@Configuration
@EnableRedisHttpSession(maxInactiveIntervalInSeconds = 86400) // 24小时过期
public class SessionConfig {

    /**
     * 配置Session Cookie的属性
     */
    @Bean
    public CookieSerializer cookieSerializer() {
        DefaultCookieSerializer serializer = new DefaultCookieSerializer();

        // Cookie名称
        serializer.setCookieName("JSESSIONID");

        // Cookie路径
        serializer.setCookiePath("/");

        // Cookie最大存活时间（秒），-1表示浏览器关闭时删除
        serializer.setCookieMaxAge(86400); // 24小时

        // 是否只能通过HTTP访问（防止XSS攻击）
        serializer.setUseHttpOnlyCookie(false); // 设为false允许前端JavaScript访问

        // 是否只在HTTPS下传输
        serializer.setUseSecureCookie(false); // 开发环境设为false，生产环境应设为true

        // 设置SameSite属性
        serializer.setSameSite("Lax");

        return serializer;
    }
}
