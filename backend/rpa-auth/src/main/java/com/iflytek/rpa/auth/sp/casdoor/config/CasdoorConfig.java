package com.iflytek.rpa.auth.sp.casdoor.config;

import org.casbin.casdoor.config.CasdoorConfiguration;
import org.casbin.casdoor.service.GroupService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * @desc: Casdoor配置类，仅在casdoor profile下生效
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 10:24
 */
@Configuration
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorConfig {

    /**
     * 创建Casdoor GroupService Bean
     * 官方Starter没有提供GroupService，需要手动创建
     * 使用@ConditionalOnMissingBean确保不重复创建
     */
    @Bean
    @ConditionalOnMissingBean
    public GroupService getCasdoorGroupService(CasdoorConfiguration config) {
        return new GroupService(config);
    }
}
