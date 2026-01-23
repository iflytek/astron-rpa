package com.iflytek.rpa.auth.sp.uap.utils;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.core.client.AuthenticationClient;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.authentication.RequestTokenResDto;
import com.iflytek.sec.uap.client.core.model.AuthenticationClientOptions;

/**
 * @author mjren
 * @date 2025-02-25 9:55
 * @copyright Copyright (c) 2025 mjren
 */
@ConditionalOnSaaSOrUAP
public class UapAuthenticationClientUtil {

    public static String getToken() {
        AuthenticationClientOptions clientOptions = new AuthenticationClientOptions();
        clientOptions.setAppAuthCode(ClientConfigUtil.instance().getAppAuthCode());
        clientOptions.setAppCode(ClientConfigUtil.instance().getAppCode());
        clientOptions.setUapHost(ClientConfigUtil.instance().getRestServerUrl()); // todo
        clientOptions.setProtocol(ClientConfigUtil.instance().getProtocol());

        AuthenticationClient authenticationClient = new AuthenticationClient(clientOptions);
        ResponseDto<RequestTokenResDto> responseDto = null;
        responseDto = authenticationClient.getUapToken();
        String token = null;
        if (responseDto.isFlag()) {
            token = ((RequestTokenResDto) responseDto.getData()).getToken();
        }
        return token;
    }
}
