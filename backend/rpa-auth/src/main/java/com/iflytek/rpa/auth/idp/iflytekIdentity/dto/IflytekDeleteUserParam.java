package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 讯飞账号删除用户参数
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekDeleteUserParam {
    private String userid;
}
