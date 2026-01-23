package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 同步用户信息 - 登录账号信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekSyncUserInfoAccount {
    private String loginid;
    private String ccode;
    private Integer lgtype;
}
