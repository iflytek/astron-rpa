package com.iflytek.rpa.market.annotation;

import com.iflytek.rpa.market.entity.MarketDto;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RightCheck {
    String dictCode() default "";

    Class<?> clazz() default MarketDto.class;

    boolean printLog() default true;
}
