package com.iflytek.rpa.auth.sp.uap.utils;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.BindResourceDto;
import com.iflytek.rpa.auth.core.entity.OrgListDto;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.authentication.RequestTokenResDto;
import com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.resource.QueryResourceDto;
import com.iflytek.sec.uap.client.core.dto.resource.UapResource;
import com.iflytek.sec.uap.client.core.model.ManagementClientOptions;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;

/**
 * @author mjren
 * @date 2025-02-24 10:56
 * @copyright Copyright (c) 2025 mjren
 */
@ConditionalOnSaaSOrUAP
public class UapManagementClientUtil {
    //    private final ManagementClientOptions options;
    //
    //    public UapManagementClientUtil(ManagementClientOptions options) {
    //        super(options);
    //        if (null == options) {
    //            throw new IllegalArgumentException("options is required");
    //        } else {
    //            this.options = options;
    //            if (StringUtils.isBlank(options.getUapHost())) {
    //                throw new IllegalArgumentException("uapHost is required");
    //            } else if (StringUtils.isBlank(options.getAppCode())) {
    //                throw new IllegalArgumentException("appCode is required");
    //            } else if (StringUtils.isBlank(options.getAppAuthCode())) {
    //                throw new IllegalArgumentException("appAuthCode is required");
    //            }
    //        }
    //    }

    private static ManagementClientOptions getManagementClientOptions() {
        ManagementClientOptions clientOptions = new ManagementClientOptions();
        clientOptions.setAppCode(ClientConfigUtil.instance().getAppCode());
        clientOptions.setAppAuthCode(ClientConfigUtil.instance().getAppAuthCode());
        clientOptions.setUapHost(ClientConfigUtil.instance().getRestServerUrl());
        return clientOptions;
    }

    public static ManagementClient getManagementClient(HttpServletRequest request) {
        ManagementClientOptions managementClientOptions = new ManagementClientOptions();
        managementClientOptions.setUapHost(ClientConfigUtil.instance().getCasServerContext());
        managementClientOptions.setAppCode(ClientConfigUtil.instance().getAppCode());
        managementClientOptions.setAppAuthCode(ClientConfigUtil.instance().getAppAuthCode());
        managementClientOptions.setTenantId(UapUserInfoAPI.getTenantId(request));
        ManagementClient managementClientWithoutToken = new ManagementClient(managementClientOptions);
        ResponseDto<RequestTokenResDto> responseDto = null;
        // 获取token
        responseDto = managementClientWithoutToken.getUapToken();
        String token = null;
        if (responseDto.isFlag()) {
            token = ((RequestTokenResDto) responseDto.getData()).getToken();
        }
        managementClientOptions.setToken(token);
        return new ManagementClient(managementClientOptions);
    }

    public static String getToken(HttpServletRequest request) {
        ManagementClientOptions managementClientOptions = new ManagementClientOptions();
        managementClientOptions.setUapHost(ClientConfigUtil.instance().getCasServerContext());
        managementClientOptions.setAppCode(ClientConfigUtil.instance().getAppCode());
        managementClientOptions.setAppAuthCode(ClientConfigUtil.instance().getAppAuthCode());
        managementClientOptions.setTenantId(UapUserInfoAPI.getTenantId(request));
        ManagementClient managementClientWithoutToken = new ManagementClient(managementClientOptions);
        ResponseDto<RequestTokenResDto> responseDto = null;
        // 获取token
        responseDto = managementClientWithoutToken.getUapToken();
        String token = null;
        if (responseDto.isFlag()) {
            return ((RequestTokenResDto) responseDto.getData()).getToken();
        }
        return null;
    }

    public static ResponseDto<List<UapResource>> queryResourceListByRoleId(String roleId, HttpServletRequest request) {
        ManagementClient managementClient = getManagementClient(request);
        QueryResourceDto dto = new QueryResourceDto();
        dto.setRoleId(roleId);
        ResponseDto<List<UapResource>> responseDto = managementClient.queryResourceListByCondition(dto);
        return responseDto;
    }

    public static ResponseDto<Object> unBindRoleResource(
            String tenantId, BindResourceDto dto, HttpServletRequest request) {
        ManagementClientOptions clientOptions = getManagementClientOptions();
        clientOptions.setTenantId(tenantId);
        clientOptions.setToken(getToken(request));
        UapManagementClient uapManagementClient = new UapManagementClient(clientOptions);
        return uapManagementClient.unbindRoleSource(dto);
    }

    public static ResponseDto<Object> dataAuthSearchPage(String tenantId, HttpServletRequest request) {
        ManagementClientOptions clientOptions = getManagementClientOptions();
        clientOptions.setTenantId(tenantId);
        clientOptions.setToken(getToken(request));
        UapManagementClient uapManagementClient = new UapManagementClient(clientOptions);
        Map<String, Object> searchDto = new HashMap<>();
        searchDto.put("pageNum", 1);
        searchDto.put("pageSize", 10);
        searchDto.put("tenantId", tenantId);
        return uapManagementClient.dataAuthSearchPage(searchDto);
    }

    public static ResponseDto<PageDto<UapOrg>> queryOrgPageList(
            String tenantId, OrgListDto dto, HttpServletRequest request) {
        ManagementClientOptions clientOptions = getManagementClientOptions();
        clientOptions.setTenantId(tenantId);
        clientOptions.setToken(getToken(request));
        UapManagementClient uapManagementClient = new UapManagementClient(clientOptions);
        return uapManagementClient.queryOrgPageList(dto);
    }

    public static List<DataAuthorityWithDimDictDto> queryDataAuthByRoleId(
            String tenantId, String roleId, HttpServletRequest request) {
        ManagementClientOptions clientOptions = getManagementClientOptions();
        clientOptions.setTenantId(tenantId);
        clientOptions.setToken(getToken(request));
        UapManagementClient uapManagementClient = new UapManagementClient(clientOptions);
        return uapManagementClient.queryDataAuthByRoleId(tenantId, roleId);
    }
}
