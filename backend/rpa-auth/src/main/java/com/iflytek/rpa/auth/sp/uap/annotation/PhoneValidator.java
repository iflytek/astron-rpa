package com.iflytek.rpa.auth.sp.uap.annotation;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

/**
 * 校验处理器：做手机号码格式验证的核心类
 */
public class PhoneValidator implements ConstraintValidator<Phone, String> {

    // 注解对象
    private Phone phone;

    // 初始化【Phone】对象
    @Override
    public void initialize(Phone constraintAnnotation) {
        phone = constraintAnnotation;
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        // 获取【Phone】对象的手机格式验证表达式
        String pattern = phone.pattern();
        Pattern compile = Pattern.compile(pattern);
        Matcher matcher = compile.matcher(value);
        return matcher.matches();
    }
}
