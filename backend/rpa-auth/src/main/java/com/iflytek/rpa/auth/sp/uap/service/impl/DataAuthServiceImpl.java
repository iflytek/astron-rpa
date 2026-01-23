package com.iflytek.rpa.auth.sp.uap.service.impl;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.Authority;
import com.iflytek.rpa.auth.core.entity.BindRoleDataAuthDto;
import com.iflytek.rpa.auth.core.service.DataAuthService;
import com.iflytek.rpa.auth.sp.uap.mapper.AuthorityMapper;
import com.iflytek.rpa.auth.sp.uap.mapper.DataAuthorityWithDimDictDtoMapper;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.authority.UapAuthority;
import com.iflytek.sec.uap.client.core.dto.dataauthority.DataAuthorityWithDimDictDto;
import com.iflytek.sec.uap.client.core.dto.role.BindDataAuthDto;
import java.util.*;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * 数据权限服务实现
 */
@Slf4j
@Service("dataAuthService")
@ConditionalOnSaaSOrUAP
public class DataAuthServiceImpl implements DataAuthService {

    @Autowired
    private AuthorityMapper authorityMapper;

    @Autowired
    private DataAuthorityWithDimDictDtoMapper dataAuthorityWithDimDictDtoMapper;

    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto>> getCheckedDataAuth(
            String roleId, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 获取全部数据权限
        //        List<DataAuthorityWithDimDictDto> dataAuthList =  UapUserInfoAPI.getDataAuthList(request);
        ResponseDto<Object> allDataAuthListResponse = UapManagementClientUtil.dataAuthSearchPage(tenantId, request);
        if (!allDataAuthListResponse.isFlag() || allDataAuthListResponse.getData() == null) {
            log.error("接口调用异常 {}", allDataAuthListResponse.getMessage());
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取数据权限失败: " + allDataAuthListResponse.getMessage());
        }
        LinkedHashMap<String, Object> data = (LinkedHashMap<String, Object>) allDataAuthListResponse.getData();
        if (null == data || null == data.get("list")) {
            log.error("获取数据权限失败: 返回数据为空");
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取数据权限失败: 返回数据为空");
        }
        List<Object> dataAuthObjectList = (List<Object>) data.get("list");
        List<DataAuthorityWithDimDictDto> dataAuthList = new ArrayList<>();
        for (Object dataAuthObj : dataAuthObjectList) {
            if (null == dataAuthObj) {
                continue;
            }
            LinkedHashMap<String, Object> dataAuthMap = (LinkedHashMap<String, Object>) dataAuthObj;
            DataAuthorityWithDimDictDto dataAuthorityWithDimDictDto = new DataAuthorityWithDimDictDto();
            dataAuthorityWithDimDictDto.setDataAuthId((String) dataAuthMap.get("id"));
            dataAuthorityWithDimDictDto.setDataAuthName((String) dataAuthMap.get("name"));
            dataAuthList.add(dataAuthorityWithDimDictDto);
        }
        // 获取勾选的数据权限
        List<DataAuthorityWithDimDictDto> checkedDataAuthList =
                UapManagementClientUtil.queryDataAuthByRoleId(tenantId, roleId, request);
        Boolean haveChecked = false;
        if (!CollectionUtils.isEmpty(checkedDataAuthList)) {
            if (checkedDataAuthList.size() > 1) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "同一模块绑定了多个数据权限");
            }
            // 获取之前绑定的模块权限
            DataAuthorityWithDimDictDto checkedDataAuth = checkedDataAuthList.get(0);
            for (DataAuthorityWithDimDictDto dataAuth : dataAuthList) {
                if (dataAuth.getDataAuthId().equals(checkedDataAuth.getDataAuthId())) {
                    dataAuth.setChecked(true);
                    haveChecked = true;
                } else {
                    dataAuth.setChecked(false);
                }
            }
        }
        if (Boolean.FALSE.equals(haveChecked)) {
            // 默认全部
            for (DataAuthorityWithDimDictDto dataAuth : dataAuthList) {
                if ("全部".equals(dataAuth.getDataAuthName())) {
                    dataAuth.setChecked(true);
                }
            }
        }
        List<com.iflytek.rpa.auth.core.entity.DataAuthorityWithDimDictDto> dataAuthorityWithDimDictDtos =
                dataAuthorityWithDimDictDtoMapper.fromUapDataAuthorityWithDimDictDtos(dataAuthList);
        return AppResponse.success(dataAuthorityWithDimDictDtos);
    }

    @Override
    public AppResponse<String> bindDataAuth(BindRoleDataAuthDto bindRoleDataAuthDto, HttpServletRequest request) {
        if (StringUtils.isBlank(bindRoleDataAuthDto.getRoleId())
                || StringUtils.isBlank(bindRoleDataAuthDto.getDataAuthId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String roleId = bindRoleDataAuthDto.getRoleId();
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        // 如果新旧数据权限id不同则需要解绑再绑定
        // 查询角色之前绑定的数据权限
        String tenantId = UapUserInfoAPI.getTenantId(request);
        List<DataAuthorityWithDimDictDto> oldBindDataAuthList =
                UapManagementClientUtil.queryDataAuthByRoleId(tenantId, roleId, request);
        if (!CollectionUtils.isEmpty(oldBindDataAuthList)) {
            // 去掉空元素
            oldBindDataAuthList.removeIf(Objects::isNull);
            if (oldBindDataAuthList.size() > 1) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "同一模块绑定了多个数据权限");
            }

            // 获取之前绑定的数据权限
            DataAuthorityWithDimDictDto oldDataAuth = oldBindDataAuthList.get(0);
            if (null != oldDataAuth) {
                if (!bindRoleDataAuthDto.getDataAuthId().equals(oldDataAuth.getDataAuthId())) {
                    // 如果变更了数据权限，则先解绑旧的数据权限
                    BindDataAuthDto bindDataAuthDto = new BindDataAuthDto();
                    bindDataAuthDto.setRoleId(roleId);
                    bindDataAuthDto.setDataAuthIdList(Collections.singletonList(oldDataAuth.getDataAuthId()));
                    ResponseDto<Object> unbindResponse = managementClient.unbindRoleDataAuth(bindDataAuthDto);
                    if (!unbindResponse.isFlag()) {
                        return AppResponse.error(ErrorCodeEnum.E_SERVICE, unbindResponse.getMessage());
                    }
                } else {
                    // 新旧数据权限相同，说明没有变更，直接返回
                    return AppResponse.success("保存成功");
                }
            }
        }
        // 数据权限有变更，绑定新数据权限
        BindDataAuthDto bindDataAuthDto = new BindDataAuthDto();
        bindDataAuthDto.setRoleId(roleId);
        bindDataAuthDto.setDataAuthIdList(Collections.singletonList(bindRoleDataAuthDto.getDataAuthId()));
        ResponseDto<Object> bindResponse = managementClient.bindRoleDataAuth(bindDataAuthDto);
        if (!bindResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, bindResponse.getMessage());
        }
        return AppResponse.success("保存成功");
    }

    @Override
    public AppResponse<List<Authority>> getAuthorityListByRoleId(
            String tenantId, String roleId, HttpServletRequest request) {
        List<UapAuthority> uapAuthorities = ClientManagementAPI.queryAuthorityListByRoleId(tenantId, roleId);
        List<Authority> authorities = authorityMapper.fromUapAuthorities(uapAuthorities);
        return AppResponse.success(authorities);
    }
}
