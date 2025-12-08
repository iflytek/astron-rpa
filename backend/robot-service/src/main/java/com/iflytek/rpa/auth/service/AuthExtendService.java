package com.iflytek.rpa.auth.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.JWSVerifier;
import com.nimbusds.jose.crypto.RSASSAVerifier;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.interfaces.RSAPublicKey;
import java.text.ParseException;
import java.util.Date;
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
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/20 19:04
 */
@Service
public class AuthExtendService extends AuthService {
    public AuthExtendService(Config config) {
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
     * casdoor的token登出接口
     * @param accessToken
     * @return
     * @throws IOException
     */
    public CasdoorResponse<String, Object> logout(String accessToken) throws IOException {
        Map<String, String> params = new HashMap<>();
        params.put("id_token_hint", accessToken);
        params.put("state", config.applicationName);

        CasdoorResponse<String, Object> resp =
                doGet("logout", params, new TypeReference<CasdoorResponse<String, Object>>() {});
        return resp;
    }

    /**
     * 支持传证书的token解析方法
     * @param token
     * @param certificate
     * @return
     */
    public User parseJwtTokenWithCertificate(String token, String certificate) {
        // parse jwt token
        SignedJWT parseJwt = null;
        try {
            parseJwt = SignedJWT.parse(token);
        } catch (ParseException e) {
            throw new AuthException("Cannot parse jwt token.", e);
        }
        // verify the jwt public key
        try {
            CertificateFactory cf = CertificateFactory.getInstance("X.509");
            X509Certificate cert =
                    (X509Certificate) cf.generateCertificate(new ByteArrayInputStream(certificate.getBytes()));
            RSAPublicKey publicKey = (RSAPublicKey) cert.getPublicKey();
            JWSVerifier verifier = new RSASSAVerifier(publicKey);
            boolean verify = parseJwt.verify(verifier);
            if (!verify) {
                throw new AuthException("Cannot verify signature.");
            }
        } catch (CertificateException | JOSEException e) {
            throw new AuthException("Cannot verify signature.", e);
        }

        // read "access_token" from payload and convert to CasdoorUser
        try {
            JWTClaimsSet claimsSet = parseJwt.getJWTClaimsSet();
            String userJson = claimsSet == null ? null : claimsSet.toString();

            if (userJson == null || userJson.isEmpty()) {
                throw new AuthException("Cannot get claims from JWT payload");
            }

            // check if the token has expired
            Date expireTime = claimsSet.getExpirationTime();
            if (expireTime.before(new Date())) {
                throw new AuthException("The token has expired");
            }

            return objectMapper.readValue(userJson, User.class);
        } catch (JsonProcessingException | java.text.ParseException e) {
            throw new AuthException("Cannot convert claims to User", e);
        }
    }
}
