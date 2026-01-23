package com.iflytek.rpa.auth.sp.uap.annotation;

import java.lang.annotation.*;
import javax.validation.Constraint;
import javax.validation.Payload;

/**
 * 手机号验证正则
 */
@Target({ElementType.FIELD, ElementType.METHOD, ElementType.PARAMETER, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Constraint(validatedBy = {PhoneValidator.class}) // 指定约束处理器，也就是手机号格式验证是哪个类来做校验
public @interface Phone {

    String pattern() default "^(?:(?:\\+|00)86)?1\\d{10}$";

    String message() default "手机号格式非法";

    Class<?>[] groups() default {}; // groups用来指定分组，可以让校验采取不同的机制，当前默认未指定任何分组机制，默认每次都要进行校验

    Class<? extends Payload>[] payload() default {};

    interface Default {}
}
