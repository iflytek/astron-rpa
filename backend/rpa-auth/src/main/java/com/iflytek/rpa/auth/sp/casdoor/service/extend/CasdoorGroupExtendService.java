package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.IOException;
import java.util.List;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.service.GroupService;
import org.casbin.casdoor.util.Map;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: 基于casdoor原生服务的群组拓展服务，仅在casdoor profile下生效
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/12 15:37
 */
@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorGroupExtendService extends GroupService {

    public CasdoorGroupExtendService(Config config) {
        super(config);
    }

    /**
     * 根据租户（casdoor的组织）名查租户下所有群组
     * @param tenantName
     * @return
     * @throws IOException
     */
    public List<Group> getGroups(String tenantName) throws IOException {
        CasdoorResponse<List<Group>, Object> response = doGet(
                "get-groups",
                Map.of("owner", tenantName),
                new TypeReference<CasdoorResponse<List<Group>, Object>>() {});
        return response.getData();
    }
}
