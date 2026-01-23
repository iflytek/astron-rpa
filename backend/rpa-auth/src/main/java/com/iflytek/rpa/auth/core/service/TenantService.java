package com.iflytek.rpa.auth.core.service;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.utils.AppResponse;
import java.io.IOException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 租户服务
 */
public interface TenantService {

    /**
     * 租户下所有用户
     * @param userName
     * @return
     * @throws Exception
     */
    AppResponse<List<UserVo>> getAllUser(String userName) throws Exception;

    /**
     * 当前登录用户在此应用的租户列表
     * @param request
     * @return
     */
    AppResponse<List<Tenant>> getTenantListInApp(HttpServletRequest request);

    /**
     * 企业信息查询
     * @param request
     * @return
     * @throws Exception
     */
    AppResponse<TenantInfoDto> getTenantInfo(HttpServletRequest request) throws Exception;

    /**
     * 获取租户ID
     * @param request
     * @return
     */
    AppResponse<String> getTenantId(HttpServletRequest request);

    /**
     * 获取当前登录的租户ID
     * @param request HTTP请求
     * @return 当前登录的租户ID
     */
    AppResponse<String> getCurrentTenantId(HttpServletRequest request);

    /**
     * 获取当前登录的租户名称
     * @param request HTTP请求
     * @return 当前登录的租户名称
     */
    AppResponse<String> getCurrentTenantName(HttpServletRequest request);

    /**
     * 根据租户ID查询租户信息
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 租户信息
     */
    AppResponse<Tenant> queryTenantInfoById(String tenantId, HttpServletRequest request) throws IOException;

    /**
     * 更改企业管理员（暂不支持）
     * @param id
     * @param request
     * @return
     */
    AppResponse<String> changeManager(String id, HttpServletRequest request);

    /**
     * 根据租户id获取所有组织列表
     * @param tenantId
     * @param request
     * @return
     */
    AppResponse<List<Org>> getAllOrgList(String tenantId, HttpServletRequest request) throws IOException;

    /**
     * 切换租户
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 切换结果
     */
    AppResponse<String> switchTenant(String tenantId, HttpServletRequest request);

    /**
     * 根据手机号查询用户所属的租户列表
     * @param phoneOrLoginName 手机号或登录名
     * @param request HTTP请求
     * @return 租户列表
     */
    AppResponse<List<Tenant>> getTenantList(String phoneOrLoginName, HttpServletRequest request);

    /**
     * 获取所有租户ID
     * @return 所有租户ID列表
     */
    AppResponse<List<String>> getAllTenantId();

    /**
     * 获取租户管理员ID列表
     * @param tenantId 租户ID
     * @return 租户管理员ID列表
     */
    AppResponse<List<String>> getTenantManagerIds(String tenantId);

    /**
     * 获取租户普通用户ID列表
     * @param tenantId 租户ID
     * @return 租户普通用户ID列表
     */
    AppResponse<List<String>> getTenantNormalUserIds(String tenantId);

    AppResponse<List<String>> getNoClassifyTenantIds();

    AppResponse<Integer> updateTenantClassifyCompleted(List<String> ids);

    /**
     * 获取所有企业租户ID列表（租户代码以ep_或es_开头）
     * @return 企业租户ID列表
     */
    AppResponse<List<String>> getAllEnterpriseTenantId();

    /**
     * 获取租户用户类型（1表示租户管理员，其他表示普通用户）
     * @param userId 用户ID
     * @param tenantId 租户ID
     * @return 租户用户类型（可能为null）
     */
    AppResponse<Integer> getTenantUserType(String userId, String tenantId);

    /**
     * 查询租户到期信息
     * 通过token获取租户，并返回到期时间、剩余时间(天)、是否到期、是否提示到期
     * @param request HTTP请求
     * @return 租户到期信息
     */
    AppResponse<TenantExpirationDto> getTenantExpiration(HttpServletRequest request);

    /**
     * 检查租户空间是否到期
     * @param request HTTP请求
     * @return true表示空间已到期，false表示空间未到期
     */
    boolean checkSpaceExpired(HttpServletRequest request);

    /**
     * 为租户填充到期信息
     * @param tenant 租户对象
     */
    void fillTenantExpirationInfo(Tenant tenant);
}
