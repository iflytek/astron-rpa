package com.iflytek.rpa.auth.sp.uap.utils;

import com.fasterxml.jackson.core.type.TypeReference;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.enums.LoginModeEnum;
import com.iflytek.rpa.auth.sp.uap.entity.LoginResultDto;
import com.iflytek.rpa.auth.utils.Sha256Utils;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.core.client.AuthenticationClient;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.enums.MethodEnum;
import com.iflytek.sec.uap.client.core.model.AuthenticationClientOptions;
import com.iflytek.sec.uap.client.core.model.UapRequestConfig;
import com.iflytek.sec.uap.client.core.util.JsonUtils;
import java.util.HashMap;
import java.util.Map;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

/**
 * ClientAuthenticationAPI 扩展类
 * 提供仅通过账号进行登录的方法
 *
 * @author lihang
 * @date 2025-11-25
 */
@Slf4j
@ConditionalOnSaaSOrUAP
public class ClientAuthenticationAPIExt extends ClientAuthenticationAPI {

    /**
     * 仅通过账号进行登录，获取 ticket
     *
     * @param loginName 登录账号
     * @param tenantId 租户ID（可选，如果为空则使用空字符串）
     * @return 登录结果，包含 ticket
     */
    public static LoginResultDto loginUapByAccount(String loginName, String tenantId) {
        // 创建 AuthenticationClient，配置会自动从 ClientConfigUtil 获取
        AuthenticationClientOptions clientOptions = new AuthenticationClientOptions();
        clientOptions.setAppAuthCode(ClientConfigUtil.instance().getAppAuthCode());
        clientOptions.setAppCode(ClientConfigUtil.instance().getAppCode());
        clientOptions.setUapHost(ClientConfigUtil.instance().getCasServerContext());
        clientOptions.setProtocol(ClientConfigUtil.instance().getProtocol());
        AuthenticationClient authenticationClient = new AuthenticationClient(clientOptions);

        // 从配置获取 appCode 和 appAuthCode，用于生成签名
        String appCode = clientOptions.getAppCode();
        String appAuthCode = clientOptions.getAppAuthCode();

        // 从配置获取 cas-client-context 作为 service
        String service = ClientConfigUtil.instance().getCasClientContext();

        // 生成时间戳
        String timeStamp = String.valueOf(System.currentTimeMillis());

        // 构建登录参数
        Map<String, String> loginParams = new HashMap<>(8);
        loginParams.put("loginName", loginName);
        loginParams.put("tenantId", StringUtils.isNotBlank(tenantId) ? tenantId : "default-tenant");
        loginParams.put("service", service);
        loginParams.put("orgId", "");
        loginParams.put("credentialType", LoginModeEnum.NOPASSWORD.getCode());
        loginParams.put("appCode", appCode);

        // 生成签名：sha256Hmac(appAuthCode, loginName + "|" + appCode + "|" + timeStamp)
        String signData = loginName + "|" + appCode + "|" + timeStamp;
        String sign = Sha256Utils.sha256Hmac(appAuthCode, signData);
        loginParams.put("sign", sign);
        loginParams.put("timeStamp", timeStamp);

        // 使用 UapRequestConfig 和 request 方法发送请求
        UapRequestConfig config = new UapRequestConfig("/api/v2/login", MethodEnum.FORM_POST, loginParams);
        String response = authenticationClient.request(config);

        // 解析响应
        ResponseDto<LoginResultDto> result =
                JsonUtils.parseObject(response, new TypeReference<ResponseDto<LoginResultDto>>() {});

        if (result == null || !result.isFlag()) {
            String errorMsg = result != null ? result.getMessage() : "登录响应解析失败";
            log.error("登录失败: {}", errorMsg);
            throw new RuntimeException("登录失败: " + errorMsg);
        }

        return result.getData();
    }

    /**
     * 仅通过账号进行登录，获取 ticket（使用默认租户ID）
     *
     * @param loginName 登录账号
     * @return 登录结果，包含 ticket
     */
    public static LoginResultDto loginUapByAccount(String loginName) {
        return loginUapByAccount(loginName, null);
    }
}
