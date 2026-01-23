package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekSendMsgCodeParam {
    private String ccode;
    private String phone;
    private int expire;
}
