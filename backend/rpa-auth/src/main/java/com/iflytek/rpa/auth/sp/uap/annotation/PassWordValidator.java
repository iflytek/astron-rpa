package com.iflytek.rpa.auth.sp.uap.annotation;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;
import org.apache.commons.lang3.StringUtils;

public class PassWordValidator implements ConstraintValidator<Password, String> {
    //        8-20位的密码，必须包含数字和字母，支持特殊符号~!@#$%^*

    //    private final String regexp = "^(?![0-9]+$)(?![a-zA-Z~!@#$%^*]+$)[0-9A-Za-z~!@#$%^*]{8,20}$";
    private final String regexp = "^[a-zA-Z0-9|\\x21-\\x2f\\x3a-\\x40\\x5b-\\x60\\x7B-\\x7F]{6,20}$";

    // 注解对象
    private Password password;

    @Override
    public void initialize(Password constraintAnnotation) {
        password = constraintAnnotation;
    }

    @Override
    public boolean isValid(String value, ConstraintValidatorContext constraintValidatorContext) {
        if (StringUtils.isBlank(value)) {
            return false;
        }
        Pattern compile = Pattern.compile(regexp);
        Matcher matcher = compile.matcher(value);
        return matcher.matches();
    }
}
