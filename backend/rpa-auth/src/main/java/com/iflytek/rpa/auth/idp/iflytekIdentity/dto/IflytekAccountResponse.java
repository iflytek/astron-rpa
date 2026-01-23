package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.Data;

@Data
public class IflytekAccountResponse<T> {
    private String code;
    private String desc;
    private T data;
}
