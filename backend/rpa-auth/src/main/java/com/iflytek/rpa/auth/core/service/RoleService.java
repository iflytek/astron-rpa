package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 角色服务接口
 */
public interface RoleService {

    /**
     * 查询应用内全部角色列表
     *
     * @param request HTTP请求
     * @return 角色列表
     */
    AppResponse<List<Role>> getUserRoleListInApp(HttpServletRequest request) throws IOException;

    /**
     * 查询当前用户角色列表
     *
     * @param request HTTP请求
     * @return 角色列表
     */
    AppResponse<List<Role>> getUserRoleList(HttpServletRequest request) throws IOException;

    /**
     * 查询角色详情
     *
     * @param dto     查询参数
     * @param request HTTP请求
     * @return 角色详情
     */
    AppResponse<Role> queryRoleDetail(GetRoleDto dto, HttpServletRequest request) throws IOException;

    /**
     * 新增角色
     *
     * @param createRoleDto 新增角色DTO
     * @param request       HTTP请求
     * @return 结果
     */
    AppResponse<String> addRole(CreateRoleDto createRoleDto, HttpServletRequest request) throws IOException;

    /**
     * 编辑角色
     *
     * @param updateRoleDto 更新角色DTO
     * @param request       HTTP请求
     * @return 结果
     */
    AppResponse<String> updateRole(UpdateRoleDto updateRoleDto, HttpServletRequest request) throws IOException;

    /**
     * 删除角色
     *
     * @param deleteCommonDto 删除角色DTO
     * @param request         HTTP请求
     * @return 删除结果
     */
    AppResponse<String> deleteRole(DeleteCommonDto deleteCommonDto, HttpServletRequest request) throws IOException;

    /**
     * 根据名称模糊查询角色
     *
     * @param listRoleDto 查询条件
     * @param request     HTTP请求
     * @return 分页结果
     */
    AppResponse<PageDto<Role>> searchRole(ListRoleDto listRoleDto, HttpServletRequest request);
}
