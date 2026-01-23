package com.iflytek.rpa.auth.sp.casdoor.service.extend;

import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.service.OrganizationService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

@Service
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorOrganizationExtendService extends OrganizationService {
    public CasdoorOrganizationExtendService(Config config) {
        super(config);
    }
}
