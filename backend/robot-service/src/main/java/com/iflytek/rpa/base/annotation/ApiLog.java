package com.iflytek.rpa.base.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * API日志记录注解
 * 用于标记需要记录入参、出参、异常和耗时的方法
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface ApiLog {

    /**
     * 操作描述
     */
    String value() default "";

    /**
     * 是否记录请求参数
     */
    boolean logParams() default true;

    /**
     * 是否记录返回结果
     */
    boolean logResult() default true;

    /**
     * 是否记录异常信息
     */
    boolean logException() default true;

    /**
     * 是否记录执行时间
     */
    boolean logTime() default true;

    /**
     * 参数最大长度（超过则截取）
     */
    int maxParamLength() default 2000;

    /**
     * 返回结果最大长度（超过则截取）
     */
    int maxResultLength() default 2000;
}
