package com.iflytek.rpa.auth.idp.iflytekIdentity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IflytekAccountRequest<T> {
    private IflytekAccountBase base;
    private T param;
}
