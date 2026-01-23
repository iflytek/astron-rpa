package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.auditRecord.constants.AuditLog;
import com.iflytek.rpa.auth.core.entity.Authority;
import com.iflytek.rpa.auth.core.entity.BindRoleDataAuthDto;
import com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto;
import com.iflytek.rpa.auth.core.service.DataAuthService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 数据权限
 */
@Slf4j
@RestController
@RequestMapping("/dataAuth")
public class DataAuthController {

    @Autowired
    private DataAuthService dataAuthService;

    /**
     * 查询勾选的数据权限
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 数据权限列表
     */
    @GetMapping("/queryCheckedDataAuth")
    public AppResponse<List<DataAuthorityWithDimDictDto>> getCheckedDataAuth(
            @RequestParam("roleId") String roleId, HttpServletRequest request) {
        return dataAuthService.getCheckedDataAuth(roleId, request);
    }

    /**
     * 角色绑定数据权限
     * @param bindRoleDataAuthDto 绑定角色数据权限DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @PostMapping("/bindDataAuth")
    @AuditLog(moduleName = "管理员权限", typeName = "编辑权限")
    public AppResponse<String> bindDataAuth(
            @RequestBody BindRoleDataAuthDto bindRoleDataAuthDto, HttpServletRequest request) {
        return dataAuthService.bindDataAuth(bindRoleDataAuthDto, request);
    }

    /**
     * 根据角色ID查权限列表
     * @param tenantId 租户ID
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 权限列表
     */
    @GetMapping("/getAuthorityListByRoleId")
    public AppResponse<List<Authority>> getAuthorityListByRoleId(
            @RequestParam("tenantId") String tenantId,
            @RequestParam("roleId") String roleId,
            HttpServletRequest request) {
        return dataAuthService.getAuthorityListByRoleId(tenantId, roleId, request);
    }
}
