package com.iflytek.rpa.auth.sp.uap.annotation;

import java.lang.annotation.*;
import javax.validation.Constraint;
import javax.validation.Payload;

/**
 * 密码校验 注解
 */
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = {PassWordValidator.class})
public @interface Password {
    // 正则表达式
    String regexp() default "";

    // 校验不通过时的提示信息
    String message() default "密码格式不正确，请输入6-20位的密码，包含数字，字母或特殊符号";

    // 分组
    Class<?>[] groups() default {};

    // 集合校验
    Class<? extends Payload>[] payload() default {};

    interface Default {}
}
