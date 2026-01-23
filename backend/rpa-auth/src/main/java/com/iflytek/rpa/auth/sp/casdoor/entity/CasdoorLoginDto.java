package com.iflytek.rpa.auth.sp.casdoor.entity;

import lombok.Data;

@Data
public class CasdoorLoginDto {
    private String application;

    private String organization;

    private String username;

    private String password;

    private Boolean autoSignin = true;

    private String language;

    /**
     * Password/LDAP/Code/Face ID
     */
    private String signinMethod = "Password";

    /**
     * login/code/token/id_token/device/saml/cas
     */
    private String type = "login";
}
