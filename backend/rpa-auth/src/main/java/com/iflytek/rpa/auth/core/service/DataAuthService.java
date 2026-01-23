package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.Authority;
import com.iflytek.rpa.auth.core.entity.BindRoleDataAuthDto;
import com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 数据权限服务
 */
public interface DataAuthService {

    /**
     * 查询勾选的数据权限
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 数据权限列表
     */
    AppResponse<List<DataAuthorityWithDimDictDto>> getCheckedDataAuth(String roleId, HttpServletRequest request);

    /**
     * 角色绑定数据权限
     * @param bindRoleDataAuthDto 绑定角色数据权限DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> bindDataAuth(BindRoleDataAuthDto bindRoleDataAuthDto, HttpServletRequest request);

    /**
     * 根据角色ID查询权限列表
     * @param tenantId 租户ID
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 权限列表
     */
    AppResponse<List<Authority>> getAuthorityListByRoleId(String tenantId, String roleId, HttpServletRequest request);
}
