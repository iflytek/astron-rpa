package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.IOException;
import java.util.List;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.UserService;
import org.casbin.casdoor.util.Map;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.casbin.casdoor.util.http.HttpClient;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: 基于casdoor原生服务的用户拓展服务，仅在casdoor profile下生效
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 10:17
 */
@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorUserExtendService extends UserService {

    public CasdoorUserExtendService(Config config) {
        super(config);
    }

    public User getUserById(String id) throws IOException {
        CasdoorResponse<User, Object> resp =
                doGet("get-user", Map.of("userId", id), new TypeReference<CasdoorResponse<User, Object>>() {});
        return objectMapper.convertValue(resp.getData(), User.class);
    }

    public List<User> getUsers(String organizationName) throws IOException {
        CasdoorResponse<List<User>, Object> resp = doGet(
                "get-users",
                Map.of("owner", organizationName),
                new TypeReference<CasdoorResponse<List<User>, Object>>() {});
        return resp.getData();
    }

    public User getUserByPhone(String phone) throws IOException {
        CasdoorResponse<User, Object> resp =
                doGet("get-user", Map.of("phone", phone), new TypeReference<CasdoorResponse<User, Object>>() {});
        return objectMapper.convertValue(resp.getData(), User.class);
    }

    /**
     * 检查用户密码是否正确
     * @param user 用户信息（包含用户名和密码）
     * @return true 如果密码正确，false 如果密码错误
     * @throws IOException 如果发生IO异常
     */
    public boolean checkUserPassword(User user) throws IOException {
        String payload = objectMapper.writeValueAsString(user);

        // 直接调用底层HTTP方法，避免doPost在status != "ok"时抛出异常
        String url = String.format("%s/api/check-user-password", config.endpoint);
        String response = HttpClient.postString(url, payload, credential);

        // 手动解析响应
        CasdoorResponse<User, Boolean> resp =
                objectMapper.readValue(response, new TypeReference<CasdoorResponse<User, Boolean>>() {});

        // 根据status判断密码是否正确
        if ("ok".equals(resp.getStatus())) {
            return true;
        } else {
            return false;
        }
    }
}
