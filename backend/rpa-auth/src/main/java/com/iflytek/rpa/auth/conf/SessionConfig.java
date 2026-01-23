package com.iflytek.rpa.auth.conf;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.session.web.http.CookieSerializer;
import org.springframework.session.web.http.DefaultCookieSerializer;

/**
 * Session Cookie 配置类
 * 用于自定义Spring Session的Cookie配置，特别是Cookie的路径
 *
 * 问题背景：
 * - 应用的context-path为 /api/rpa-auth
 * - 默认情况下，Spring Session会将Cookie的path设置为context-path
 * - 这样会导致Cookie只在 /api/rpa-auth 下生效，无法在 /api/ 下的其他应用中使用
 * - 通过此配置，强制将Cookie的path设置为 /api/，实现Cookie的跨应用共享
 *
 * 注意：此Java配置的优先级高于YAML配置，确保Cookie路径一定是 /api/
 *
 * @author lihang
 * @date 2025-12-08
 */
@Configuration
public class SessionConfig {

    /**
     * 配置Session Cookie的序列化器
     * 强制设置Cookie的path为 /api/，覆盖默认的context-path配置
     *
     * @return CookieSerializer实例
     */
    @Bean
    public CookieSerializer cookieSerializer() {
        DefaultCookieSerializer serializer = new DefaultCookieSerializer();

        // 强制设置Cookie路径为 /api/，而不是默认的context-path (/api/rpa-auth)
        // 这样Cookie可以在 /api/ 路径下的所有微服务间共享
        serializer.setCookiePath("/");

        // Cookie名称，Spring Session默认为SESSION
        serializer.setCookieName("SESSION");

        // Cookie最大存活时间（秒），与@EnableRedisHttpSession的maxInactiveIntervalInSeconds保持一致
        // 604800秒 = 7天
        //        serializer.setCookieMaxAge(604800);

        // 启用HttpOnly，防止JavaScript访问Cookie，提高安全性
        serializer.setUseHttpOnlyCookie(true);

        // 是否启用Secure（仅在HTTPS下传输Cookie）
        // 开发环境可以不启用，生产环境建议启用
        // serializer.setUseSecureCookie(true);

        // SameSite属性，防止CSRF攻击
        // Lax: 允许部分第三方请求携带Cookie（GET请求）
        // Strict: 完全禁止第三方请求携带Cookie
        // None: 允许所有第三方请求携带Cookie（需要同时设置Secure=true）
        serializer.setSameSite("Lax");

        return serializer;
    }
}
