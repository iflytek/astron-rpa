package com.iflytek.rpa.base.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 排除API日志记录注解
 * 用于标记不需要记录日志的方法（如轮询接口等高频调用的方法）
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface NoApiLog {

    /**
     * 排除原因说明
     */
    String value() default "";
}
