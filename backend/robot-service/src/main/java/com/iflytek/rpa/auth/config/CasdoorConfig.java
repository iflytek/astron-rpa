package com.iflytek.rpa.auth.config;

import org.casbin.casdoor.config.CasdoorConfiguration;
import org.casbin.casdoor.service.GroupService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Casdoor配置类 - 补充官方Starter未提供的服务
 */
@Configuration
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
