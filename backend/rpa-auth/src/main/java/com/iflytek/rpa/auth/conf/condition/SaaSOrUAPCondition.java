package com.iflytek.rpa.auth.conf.condition;

import com.iflytek.rpa.auth.core.entity.enums.DeploymentMode;
import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;
import org.springframework.util.StringUtils;

/**
 * 条件判断：当部署模式为 saas 或 private-uap 时返回 true
 * 如果配置缺失，默认视为 saas 模式
 *
 * @author system
 */
public class SaaSOrUAPCondition implements Condition {

    private static final String DEPLOYMENT_MODE_PROPERTY = "rpa.auth.deployment-mode";
    private static final String DEFAULT_MODE = "saas";

    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        String deploymentMode = context.getEnvironment().getProperty(DEPLOYMENT_MODE_PROPERTY);

        // 如果配置缺失，默认视为 saas 模式（matchIfMissing = true）
        if (!StringUtils.hasText(deploymentMode)) {
            deploymentMode = DEFAULT_MODE;
        }

        // 判断是否为 saas 或 private-uap 模式
        return DeploymentMode.SAAS.getCode().equalsIgnoreCase(deploymentMode)
                || DeploymentMode.PRIVATE_UAP.getCode().equalsIgnoreCase(deploymentMode);
    }
}
