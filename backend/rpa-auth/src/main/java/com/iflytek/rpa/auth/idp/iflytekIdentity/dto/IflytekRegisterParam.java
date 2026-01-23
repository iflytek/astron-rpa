package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekRegisterParam {
    private String loginid;
    private int lgtype;
    private String ccode;
    private String password;
    private String pwdtype;
}
