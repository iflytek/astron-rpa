package com.iflytek.rpa.auth.sp.casdoor.entity;

import lombok.Data;

/**
 * Casdoor 注册请求参数
 */
@Data
public class CasdoorSignupDto {
    private String application;
    private String organization;
    private String username;
    private String password;
    private String name;
    private String phone;
    private String countryCode;
}
