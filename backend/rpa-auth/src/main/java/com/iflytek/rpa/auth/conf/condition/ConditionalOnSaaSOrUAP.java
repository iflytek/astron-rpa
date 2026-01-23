package com.iflytek.rpa.auth.conf.condition;

import java.lang.annotation.*;
import org.springframework.context.annotation.Conditional;

/**
 * 条件注解：当部署模式为 saas 或 private-uap 时生效
 * 如果配置缺失，默认视为 saas 模式（matchIfMissing = true）
 *
 * @author system
 */
@Target({ElementType.TYPE, ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Conditional(SaaSOrUAPCondition.class)
public @interface ConditionalOnSaaSOrUAP {}
