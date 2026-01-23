package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import com.iflytek.rpa.auth.core.entity.Authority;
import com.iflytek.rpa.auth.core.entity.BindRoleDataAuthDto;
import com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto;
import com.iflytek.rpa.auth.core.service.DataAuthService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.ArrayList;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/11 17:50
 */
@Slf4j
@Service("casdoorDataAuthService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorDataAuthServiceImpl implements DataAuthService {
    @Override
    public AppResponse<List<DataAuthorityWithDimDictDto>> getCheckedDataAuth(
            String roleId, HttpServletRequest request) {
        return AppResponse.success(new ArrayList<>());
    }

    @Override
    public AppResponse<String> bindDataAuth(BindRoleDataAuthDto bindRoleDataAuthDto, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<List<Authority>> getAuthorityListByRoleId(
            String tenantId, String roleId, HttpServletRequest request) {
        return AppResponse.success(new ArrayList<>());
    }
}
