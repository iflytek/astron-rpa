package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import org.apache.oltu.oauth2.client.OAuthClient;
import org.apache.oltu.oauth2.client.URLConnectionClient;
import org.apache.oltu.oauth2.client.request.OAuthClientRequest;
import org.apache.oltu.oauth2.client.response.OAuthJSONAccessTokenResponse;
import org.apache.oltu.oauth2.common.OAuth;
import org.apache.oltu.oauth2.common.exception.OAuthProblemException;
import org.apache.oltu.oauth2.common.exception.OAuthSystemException;
import org.apache.oltu.oauth2.common.message.types.GrantType;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: 基于casdoor原生服务的权限拓展服务，仅在casdoor profile下生效
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 10:17
 */
@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorAuthExtendService extends AuthService {
    public CasdoorAuthExtendService(Config config) {
        super(config);
    }

    public String getCustomSigninUrl(String redirectUrl) {
        return this.getCustomSigninUrl(redirectUrl, config.applicationName);
    }

    public String getCustomSigninUrl(String redirectUrl, String state) {
        String scope = "read";
        try {
            return String.format(
                    "/login/oauth/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=%s&state=%s",
                    config.clientId, URLEncoder.encode(redirectUrl, StandardCharsets.UTF_8.toString()), scope, state);
        } catch (UnsupportedEncodingException e) {
            throw new AuthException(e);
        }
    }

    public OAuthJSONAccessTokenResponse getOAuthTokenResponse(String code, String state) {
        try {
            OAuthClientRequest oAuthClientRequest = OAuthClientRequest.tokenLocation(
                            String.format("%s/api/login/oauth/access_token", this.config.endpoint))
                    .setGrantType(GrantType.AUTHORIZATION_CODE)
                    .setClientId(this.config.clientId)
                    .setClientSecret(this.config.clientSecret)
                    .setRedirectURI(String.format("%s/api/login/oauth/authorize", this.config.endpoint))
                    .setCode(code)
                    .buildQueryMessage();
            OAuthClient oAuthClient = new OAuthClient(new URLConnectionClient());
            return oAuthClient.accessToken(oAuthClientRequest, "POST");
        } catch (OAuthProblemException | OAuthSystemException var6) {
            Exception e = var6;
            throw new AuthException("Cannot get OAuth token.", e);
        }
    }

    public OAuthJSONAccessTokenResponse getOAuthTokenResponse1(String code, String state) {
        try {
            OAuthClientRequest oAuthClientRequest = OAuthClientRequest.tokenLocation(
                            String.format("%s/api/login/oauth/access_token", config.endpoint))
                    .setGrantType(GrantType.AUTHORIZATION_CODE)
                    .setClientId(config.clientId)
                    .setClientSecret(config.clientSecret)
                    .setRedirectURI(String.format("%s/api/login/oauth/authorize", config.endpoint))
                    .setCode(code)
                    .buildQueryMessage();
            OAuthClient oAuthClient = new OAuthClient(new URLConnectionClient());
            return oAuthClient.accessToken(oAuthClientRequest, OAuth.HttpMethod.POST);
        } catch (OAuthSystemException | OAuthProblemException e) {
            throw new AuthException("Cannot get OAuth token.", e);
        }
    }

    public OAuthJSONAccessTokenResponse refreshToken(String refreshToken, String scope) {
        try {
            OAuthClientRequest oAuthClientRequest = OAuthClientRequest.tokenLocation(
                            String.format("%s/api/login/oauth/refresh_token", config.endpoint))
                    .setGrantType(GrantType.REFRESH_TOKEN)
                    .setClientId(config.clientId)
                    .setClientSecret(config.clientSecret)
                    .setRefreshToken(refreshToken)
                    .setScope(scope)
                    .buildQueryMessage();
            OAuthClient oAuthClient = new OAuthClient(new URLConnectionClient());
            return oAuthClient.accessToken(oAuthClientRequest, OAuth.HttpMethod.POST);
        } catch (OAuthSystemException | OAuthProblemException e) {
            throw new AuthException("Cannot refresh OAuth token.", e);
        }
    }

    /**
     * casdoor的token登出接口(仅测试用，完整的logout接口参考CasdoorLoginExtendService)
     * @param accessToken
     * @return
     * @throws IOException
     */
    public CasdoorResponse<String, Object> logout(String accessToken) throws IOException {
        Map<String, String> params = new HashMap<>();
        params.put("id_token_hint", accessToken);
        params.put("state", config.applicationName);

        CasdoorResponse<String, Object> resp =
                this.doPost("logout", params, new HashMap<>(), new TypeReference<CasdoorResponse<String, Object>>() {});
        return resp;
    }
}
