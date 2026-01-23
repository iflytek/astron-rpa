package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.auditRecord.constants.AuditLog;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.RoleService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 角色
 */
@RestController
@RequestMapping("/role")
@Slf4j
public class RoleController {

    @Autowired
    private RoleService roleService;

    /**
     * 查询应用内全部角色列表
     *
     * @param request 请求
     * @return 角色列表
     */
    @GetMapping("/getUserRoleListInApp")
    public AppResponse<List<Role>> queryTreeList(HttpServletRequest request) throws IOException {
        return roleService.getUserRoleListInApp(request);
    }

    /**
     * 查询角色列表
     *
     * @param request 请求
     * @return 角色列表
     */
    @GetMapping("/getUserRoleList")
    public AppResponse<List<Role>> queryRoleList(HttpServletRequest request) throws IOException {
        return roleService.getUserRoleList(request);
    }

    /**
     * 查询角色详情
     *
     * @param dto     查询参数
     * @param request 请求
     * @return 角色详情
     */
    @PostMapping("/queryDetail")
    public AppResponse<Role> queryRoleDetail(@RequestBody GetRoleDto dto, HttpServletRequest request)
            throws IOException {
        return roleService.queryRoleDetail(dto, request);
    }

    /**
     * 新增角色
     *
     * @param createRoleDto 新增角色DTO
     * @param request       请求
     * @return 结果
     */
    @AuditLog(moduleName = "管理员权限", typeName = "创建角色")
    @PostMapping("/add")
    public AppResponse<String> addRole(@RequestBody CreateRoleDto createRoleDto, HttpServletRequest request)
            throws IOException {
        return roleService.addRole(createRoleDto, request);
    }

    /**
     * 编辑角色
     *
     * @param updateRoleDto 更新角色DTO
     * @param request       请求
     * @return 结果
     */
    @PostMapping("/update")
    public AppResponse<String> updateRole(@RequestBody UpdateRoleDto updateRoleDto, HttpServletRequest request)
            throws IOException {
        return roleService.updateRole(updateRoleDto, request);
    }

    /**
     * 删除角色
     *
     * @param deleteCommonDto 删除角色DTO
     * @param request         HTTP请求
     * @return 删除结果
     */
    @AuditLog(moduleName = "管理员权限", typeName = "删除角色")
    @PostMapping("/delete")
    public AppResponse<String> deleteRole(@RequestBody DeleteCommonDto deleteCommonDto, HttpServletRequest request)
            throws IOException {
        return roleService.deleteRole(deleteCommonDto, request);
    }

    /**
     * 根据名称模糊查询角色
     *
     * @param listRoleDto 查询条件
     * @param request     请求
     * @return 分页结果
     */
    @PostMapping("/search")
    public AppResponse<PageDto<Role>> searchRole(@RequestBody ListRoleDto listRoleDto, HttpServletRequest request) {
        return roleService.searchRole(listRoleDto, request);
    }
}
