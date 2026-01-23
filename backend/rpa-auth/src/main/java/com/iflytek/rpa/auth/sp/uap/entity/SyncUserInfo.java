package com.iflytek.rpa.auth.sp.uap.entity;

import lombok.Data;

/**
 * 同步用户信息实体
 */
@Data
public class SyncUserInfo {
    /**
     * 用户ID
     */
    private String id;

    /**
     * 登录名
     */
    private String loginName;

    /**
     * 用户姓名
     */
    private String name;

    /**
     * 手机号
     */
    private String phone;

    /**
     * 地址
     */
    private String address;
}
