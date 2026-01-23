package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * 同步用户信息 - 用户详细信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekSyncUserInfoUserInfo {
    private String nickname;
    private String headpic;
    private String sign;
    private String sex;
    private String address;
    private Map<String, Object> extras;
}

