package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorLoginDto;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorLoginResult;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorSignupDto;
import java.io.IOException;
import java.net.URLEncoder;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

@Slf4j
@org.springframework.stereotype.Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorLoginExtendService {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private Config config;

    private final RestTemplate restTemplate = new RestTemplate();

    public CasdoorLoginResult login(CasdoorLoginDto loginDto) throws IOException {
        // 填充默认 application
        if (loginDto.getApplication() == null || loginDto.getApplication().isEmpty()) {
            loginDto.setApplication(config.applicationName);
        }

        // 构建 URL
        String endpoint = config.endpoint.replaceAll("/$", "");
        String url = endpoint + "/api/login?clientId=" + URLEncoder.encode(config.clientId, "UTF-8")
                + "&responseType=scope&redirectUri=";

        // 发送请求
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String requestBody = objectMapper.writeValueAsString(loginDto);
        ResponseEntity<String> response =
                restTemplate.exchange(url, HttpMethod.POST, new HttpEntity<>(requestBody, headers), String.class);

        // 解析响应
        CasdoorResponse<String, String> casdoorResponse =
                objectMapper.readValue(response.getBody(), new TypeReference<CasdoorResponse<String, String>>() {});

        // 检查状态
        if (!"ok".equals(casdoorResponse.getStatus())) {
            throw new IOException("登录失败: " + (casdoorResponse.getMsg() != null ? casdoorResponse.getMsg() : "未知错误"));
        }

        // 提取结果
        String userId = casdoorResponse.getData();
        if (userId == null || userId.isEmpty()) {
            throw new IOException("登录响应中未包含用户ID");
        }

        // 提取 Set-Cookie 中的 casdoor_session_id
        String casdoorSessionId = extractCasdoorSessionId(response);

        CasdoorLoginResult result = new CasdoorLoginResult();
        result.setUserId(userId);
        result.setSession(casdoorSessionId);
        return result;
    }

    public CasdoorLoginResult signup(CasdoorSignupDto signupDto) throws IOException {
        // 填充默认值
        if (signupDto.getApplication() == null || signupDto.getApplication().isEmpty()) {
            signupDto.setApplication(config.applicationName);
        }
        if (signupDto.getOrganization() == null || signupDto.getOrganization().isEmpty()) {
            signupDto.setOrganization(config.organizationName);
        }

        // 构建 URL
        String endpoint = config.endpoint.replaceAll("/$", "");
        String url = endpoint + "/api/signup";

        // 发送请求
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        String requestBody = objectMapper.writeValueAsString(signupDto);
        ResponseEntity<String> response =
                restTemplate.exchange(url, HttpMethod.POST, new HttpEntity<>(requestBody, headers), String.class);

        // 解析响应
        CasdoorResponse<String, String> casdoorResponse =
                objectMapper.readValue(response.getBody(), new TypeReference<CasdoorResponse<String, String>>() {});

        // 检查状态
        if (!"ok".equals(casdoorResponse.getStatus())) {
            throw new IOException("注册失败: " + (casdoorResponse.getMsg() != null ? casdoorResponse.getMsg() : "未知错误"));
        }

        // 提取结果
        String userId = casdoorResponse.getData();
        if (userId == null || userId.isEmpty()) {
            throw new IOException("注册响应中未包含用户ID");
        }

        CasdoorLoginResult result = new CasdoorLoginResult();
        result.setUserId(userId);
        return result;
    }

    /**
     * 从响应头中提取 casdoor_session_id
     * Casdoor 返回的 cookie 格式：casdoor_session_id=dbf0c10e8a8486c61a612a69594df0cc
     */
    private String extractCasdoorSessionId(ResponseEntity<String> response) {
        List<String> cookies = response.getHeaders().get("Set-Cookie");
        if (cookies == null || cookies.isEmpty()) {
            return null;
        }

        // 查找 casdoor_session_id
        for (String cookie : cookies) {
            String[] parts = cookie.split(";");
            if (parts.length > 0) {
                String pair = parts[0].trim();
                if (pair.startsWith("casdoor_session_id=")) {
                    return pair.substring("casdoor_session_id=".length());
                }
            }
        }

        return null;
    }

    /**
     * 从请求中提取 casdoor_session_id
     * HTTP 请求中的 Cookie 格式：Cookie: casdoor_session_id=dbf0c10e8a8486c61a612a69594df0cc; other_cookie=value
     *
     * @param request HTTP 请求
     * @return Casdoor session ID，如果未找到则返回 null
     */
    public String extractCasdoorSessionIdFromRequest(HttpServletRequest request) {
        if (request == null) {
            return null;
        }

        // 从请求头中获取 Cookie 字符串
        String cookieHeader = request.getHeader("Cookie");
        if (cookieHeader == null || cookieHeader.isEmpty()) {
            return null;
        }

        // 解析 Cookie 字符串，查找 casdoor_session_id
        String[] cookies = cookieHeader.split(";");
        for (String cookie : cookies) {
            String pair = cookie.trim();
            if (pair.startsWith("casdoor_session_id=")) {
                return pair.substring("casdoor_session_id=".length());
            }
        }

        return null;
    }

    /**
     * 调用 Casdoor 登出接口
     *
     * @param casdoorSessionId Casdoor session ID
     * @throws IOException
     */
    public void logout(String casdoorSessionId) throws IOException {
        if (casdoorSessionId == null || casdoorSessionId.isEmpty()) {
            log.warn("Casdoor session ID 为空，跳过登出");
            return;
        }

        // 构建 URL
        String endpoint = config.endpoint.replaceAll("/$", "");
        String url = endpoint + "/api/logout";

        // 设置请求头
        HttpHeaders headers = new HttpHeaders();
        headers.set("Cookie", "casdoor_session_id=" + casdoorSessionId);

        // 发送 POST 请求（无请求体）
        ResponseEntity<String> response =
                restTemplate.exchange(url, HttpMethod.POST, new HttpEntity<>(headers), String.class);

        // 解析响应
        CasdoorResponse<String, Object> casdoorResponse =
                objectMapper.readValue(response.getBody(), new TypeReference<CasdoorResponse<String, Object>>() {});

        // 检查状态
        if (!"ok".equals(casdoorResponse.getStatus())) {
            log.warn("Casdoor 登出失败: {}", casdoorResponse.getMsg());
            throw new IOException(
                    "Casdoor 登出失败: " + (casdoorResponse.getMsg() != null ? casdoorResponse.getMsg() : "未知错误"));
        }

        log.info("Casdoor 登出成功");
    }
}
