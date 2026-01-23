package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import java.util.Map;
import lombok.Data;

@Data
public class IflytekLoginData {
    private String userid;
    private String nickname;
    private Integer nkstatus;
    private String headpic;
    private String sign;
    private String sex;
    private String address;
    private Long cttime;
    private Map<String, Object> extras;
}
