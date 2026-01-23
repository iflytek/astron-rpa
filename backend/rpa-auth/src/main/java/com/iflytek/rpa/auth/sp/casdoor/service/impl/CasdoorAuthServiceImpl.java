package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import com.iflytek.rpa.auth.core.entity.RoleAuthResourceDto;
import com.iflytek.rpa.auth.core.entity.TreeNode;
import com.iflytek.rpa.auth.core.service.AuthService;
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
@Service("casdoorAuthService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorAuthServiceImpl implements AuthService {
    @Override
    public AppResponse<List<TreeNode>> getUserAuthTreeInApp(HttpServletRequest request) {
        return AppResponse.success(new ArrayList<>());
    }

    @Override
    public AppResponse<TreeNode> getAuthResourceTreeInApp(String roleId, HttpServletRequest request) {
        return AppResponse.success(new TreeNode());
    }

    @Override
    public AppResponse<String> saveRoleAuth(RoleAuthResourceDto roleAuthResourceDto, HttpServletRequest request) {
        return AppResponse.success("");
    }
}
