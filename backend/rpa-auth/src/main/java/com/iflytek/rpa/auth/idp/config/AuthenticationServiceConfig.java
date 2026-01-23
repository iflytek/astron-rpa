package com.iflytek.rpa.auth.idp.config;

import com.iflytek.rpa.auth.idp.AuthenticationService;
import javax.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;

/**
 * 认证服务配置类
 * 根据配置自动加载对应的 AuthenticationService 实现
 */
@Slf4j
@Configuration
@RequiredArgsConstructor
public class AuthenticationServiceConfig {

    private final AuthenticationProperties authProperties;

    @Autowired(required = false)
    private AuthenticationService authenticationService;

    @PostConstruct
    public void init() {
        if (authenticationService == null) {
            log.error("未找到匹配的 AuthenticationService 实现！当前部署模式：{}", authProperties.getDeploymentMode());
            throw new IllegalStateException("未找到匹配的 AuthenticationService 实现，请检查配置：rpa.auth.deployment-mode="
                    + authProperties.getDeploymentMode());
        }

        log.info("=================================================");
        log.info("认证服务初始化完成");
        log.info(
                "部署模式：{} ({})",
                authProperties.getDeploymentModeEnum().getCode(),
                authProperties.getDeploymentModeEnum().getDescription());
        log.info("认证服务实现：{}", authenticationService.getClass().getSimpleName());
        log.info("=================================================");
    }
}
