package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.RoleAuthResourceDto;
import com.iflytek.rpa.auth.core.entity.TreeNode;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 权限服务
 */
public interface AuthService {

    /**
     * 当前登录用户在应用中的菜单信息
     * @param request HTTP请求
     * @return 菜单树列表
     */
    AppResponse<List<TreeNode>> getUserAuthTreeInApp(HttpServletRequest request);

    /**
     * 查询菜单、权限树
     * @param roleId 角色ID
     * @param request HTTP请求
     * @return 菜单权限树
     */
    AppResponse<TreeNode> getAuthResourceTreeInApp(String roleId, HttpServletRequest request);

    /**
     * 保存菜单、资源树
     * @param roleAuthResourceDto 角色权限资源DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    AppResponse<String> saveRoleAuth(RoleAuthResourceDto roleAuthResourceDto, HttpServletRequest request);
}
