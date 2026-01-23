package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekLoginParam {
    private String loginid;
    private String ccode;
    private String lgtype;
    private String password;
    private String pwdtype;
}
