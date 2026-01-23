package com.iflytek.rpa.conf.entity.vo;

import lombok.Data;

/**
 * 用户注册返回VO
 */
@Data
public class UserRegisterVo {
    /**
     * 账号（手机号）
     */
    private String account;

    /**
     * 默认密码
     */
    private String password;

    private String userId;

    private String url;
}
