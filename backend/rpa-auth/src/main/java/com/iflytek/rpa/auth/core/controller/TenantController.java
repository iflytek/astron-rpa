package com.iflytek.rpa.auth.core.controller;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 租户
 */
@RestController
@RequestMapping("/tenant")
public class TenantController {

    @Autowired
    TenantService tenantService;

    /**
     * 当前登录用户在此应用的租户列表
     * @param request
     * @return
     */
    @GetMapping("/getTenantListInApp")
    public AppResponse<List<Tenant>> getTenantListInApp(HttpServletRequest request) {
        return tenantService.getTenantListInApp(request);
    }

    /**
     * 企业信息查询
     * @param request
     * @return
     */
    @GetMapping("/getTenantInfo")
    public AppResponse<TenantInfoDto> getTenantInfo(HttpServletRequest request) throws Exception {
        return tenantService.getTenantInfo(request);
    }

    /**
     * 获取租户ID
     * @param request
     * @return
     */
    @GetMapping("/getTenantId")
    public AppResponse<String> getTenantId(HttpServletRequest request) {
        return tenantService.getTenantId(request);
    }

    /**
     * 更改企业管理员（暂不支持）
     * @param request
     * @return
     */
    @GetMapping("/changeManager")
    public AppResponse<String> changeManager(@RequestParam("id") String id, HttpServletRequest request) {
        return tenantService.changeManager(id, request);
    }

    @PostMapping("/all-user")
    public AppResponse<List<UserVo>> getAllUser(@RequestParam String userName) throws Exception {
        return tenantService.getAllUser(userName);
    }

    /**
     * 根据租户id获取所有组织列表
     * @param tenantId
     * @param request
     * @return
     */
    @GetMapping("/getAllOrgList")
    public AppResponse<List<Org>> getAllOrgList(@RequestParam("tenantId") String tenantId, HttpServletRequest request)
            throws IOException {
        return tenantService.getAllOrgList(tenantId, request);
    }

    /**
     * 获取当前登录的租户ID
     * @param request HTTP请求
     * @return 当前登录的租户ID
     */
    @GetMapping("/current/id")
    public AppResponse<String> getCurrentTenantId(HttpServletRequest request) {
        return tenantService.getCurrentTenantId(request);
    }

    /**
     * 获取当前登录的租户名称
     * @param request HTTP请求
     * @return 当前登录的租户名称
     */
    @GetMapping("/current/name")
    public AppResponse<String> getCurrentTenantName(HttpServletRequest request) {
        return tenantService.getCurrentTenantName(request);
    }

    /**
     * 根据租户ID查询租户信息
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 租户信息
     */
    @GetMapping("/info")
    public AppResponse<Tenant> queryTenantInfoById(
            @RequestParam("tenantId") String tenantId, HttpServletRequest request) throws IOException {
        return tenantService.queryTenantInfoById(tenantId, request);
    }

    /**
     * 切换租户
     * @param tenantId 切换租户id
     * @param request HTTP请求
     * @return 切换结果
     */
    @PostMapping("/switch")
    public AppResponse<String> switchTenant(@RequestParam("tenantId") String tenantId, HttpServletRequest request) {
        return tenantService.switchTenant(tenantId, request);
    }

    /**
     * 获取所有租户ID
     * @return 所有租户ID列表
     */
    @GetMapping("/getAllTenantId")
    public AppResponse<List<String>> getAllTenantId() {
        return tenantService.getAllTenantId();
    }

    /**
     * 获取租户管理员ID列表
     * @param tenantId 租户ID
     * @return 租户管理员ID列表
     */
    @GetMapping("/getTenantManagerIds")
    public AppResponse<List<String>> getTenantManagerIds(@RequestParam("tenantId") String tenantId) {
        return tenantService.getTenantManagerIds(tenantId);
    }

    /**
     * 获取租户普通用户ID列表
     * @param tenantId 租户ID
     * @return 租户普通用户ID列表
     */
    @GetMapping("/getTenantNormalUserIds")
    public AppResponse<List<String>> getTenantNormalUserIds(@RequestParam("tenantId") String tenantId) {
        return tenantService.getTenantNormalUserIds(tenantId);
    }

    @GetMapping("/getNoClassifyTenantIds")
    public AppResponse<List<String>> getNoClassifyTenantIds() {
        return tenantService.getNoClassifyTenantIds();
    }

    @PostMapping("/updateTenantClassifyCompleted")
    public AppResponse<Integer> updateTenantClassifyCompleted(@RequestBody List<String> ids) throws Exception {
        return tenantService.updateTenantClassifyCompleted(ids);
    }

    /**
     * 获取所有企业租户ID列表（租户代码以ep_或es_开头）
     * @return 企业租户ID列表
     */
    @GetMapping("/getAllEnterpriseTenantId")
    public AppResponse<List<String>> getAllEnterpriseTenantId() {
        return tenantService.getAllEnterpriseTenantId();
    }

    /**
     * 获取租户用户类型（1表示租户管理员，其他表示普通用户）
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @return 租户用户类型（可能为null）
     */
    @GetMapping("/getTenantUserType")
    public AppResponse<Integer> getTenantUserType(
            @RequestParam("userId") String userId, @RequestParam("tenantId") String tenantId) {
        return tenantService.getTenantUserType(userId, tenantId);
    }

    /**
     * 查询租户到期信息
     * 通过token获取租户，并返回到期时间、剩余时间(天)、是否到期、是否提示到期
     * @param request HTTP请求
     * @return 租户到期信息
     */
    @GetMapping("/expiration")
    public AppResponse<TenantExpirationDto> getTenantExpiration(HttpServletRequest request) {
        return tenantService.getTenantExpiration(request);
    }
}
