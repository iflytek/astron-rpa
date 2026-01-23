package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import com.iflytek.rpa.auth.sp.casdoor.entity.ApplicationExtend;
import java.io.IOException;
import java.util.HashMap;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.service.ApplicationService;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/1 10:57
 */
@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class ApplicationExtendService extends ApplicationService {

    public ApplicationExtendService(Config config) {
        super(config);
    }

    public ApplicationExtend getApplicationWithKey(String name) throws IOException {
        java.util.Map<String, String> params = new HashMap<>();
        params.put("id", "admin/" + name);
        params.put("withKey", "1");

        CasdoorResponse<ApplicationExtend, Object> response =
                doGet("get-application", params, new TypeReference<CasdoorResponse<ApplicationExtend, Object>>() {});
        return response.getData();
    }
}
