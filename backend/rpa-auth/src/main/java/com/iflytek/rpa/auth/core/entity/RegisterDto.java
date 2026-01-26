package com.iflytek.rpa.auth.core.entity;

import com.iflytek.rpa.auth.sp.uap.annotation.Phone;
import lombok.Builder;
import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * @author mjren
 * @date 2025-03-24 11:28
 * @copyright Copyright (c) 2025 mjren
 */
@Data
@Builder
public class RegisterDto {

    private String captcha;

    private String loginName;

    private String phone;

    private String password;

    private String confirmPassword;

}
