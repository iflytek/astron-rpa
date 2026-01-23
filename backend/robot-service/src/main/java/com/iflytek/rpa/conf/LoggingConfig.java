package com.iflytek.rpa.conf;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

/**
 * 日志配置类
 * 启用AspectJ代理以支持AOP功能
 */
@Configuration
@EnableAspectJAutoProxy(proxyTargetClass = true)
public class LoggingConfig {

    // 该配置类确保AOP切面能够正常工作
    // @EnableAspectJAutoProxy(proxyTargetClass = true) 启用CGLIB代理，
    // 这样可以对没有实现接口的类也进行代理
}
