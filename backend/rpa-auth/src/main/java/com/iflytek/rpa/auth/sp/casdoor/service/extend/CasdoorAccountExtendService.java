package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.IOException;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.entity.Organization;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.AccountService;
import org.casbin.casdoor.util.Map;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;

@org.springframework.stereotype.Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorAccountExtendService extends AccountService {
    public CasdoorAccountExtendService(Config config) {
        super(config);
    }

    public CasdoorResponse<User, Organization> getAccountBySession(String session) throws IOException {
        return doGet(
                "get-account",
                Map.of("access_token", session),
                new TypeReference<CasdoorResponse<User, Organization>>() {});
    }
}
