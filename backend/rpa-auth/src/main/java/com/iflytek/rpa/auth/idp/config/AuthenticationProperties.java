package com.iflytek.rpa.auth.idp.config;

import com.iflytek.rpa.auth.core.entity.enums.DeploymentMode;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 认证配置属性
 */
@Data
@Component
@ConfigurationProperties(prefix = "rpa.auth")
public class AuthenticationProperties {

    /**
     * 部署模式：saas | private-enterprise | private-uap | casdoor
     * 默认为 saas
     */
    private String deploymentMode = "casdoor";

    /**
     * 获取部署模式枚举
     */
    public DeploymentMode getDeploymentModeEnum() {
        return DeploymentMode.fromCode(deploymentMode);
    }
}
