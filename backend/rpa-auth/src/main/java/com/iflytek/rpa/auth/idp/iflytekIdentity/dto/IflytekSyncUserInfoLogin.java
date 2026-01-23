package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 同步用户信息 - 登录信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekSyncUserInfoLogin {
    private List<IflytekSyncUserInfoAccount> account;
}
