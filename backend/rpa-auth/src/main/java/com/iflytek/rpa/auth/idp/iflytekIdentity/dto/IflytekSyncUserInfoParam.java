package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 同步用户信息 - 请求参数
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekSyncUserInfoParam {
    private String userid;
    private String password;
    private IflytekSyncUserInfoLogin login;
    private IflytekSyncUserInfoUserInfo userinfo;
}
