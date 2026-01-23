package com.iflytek.rpa.auth.sp.uap.service.impl;

import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.RoleService;
import com.iflytek.rpa.auth.sp.uap.dao.RoleDao;
import com.iflytek.rpa.auth.sp.uap.mapper.*;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.HttpUtils;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.app.UapApp;
import com.iflytek.sec.uap.client.core.dto.role.UapRole;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import com.iflytek.sec.uap.client.util.Oauth2Util;
import java.util.List;
import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * 角色服务实现类
 */
@Slf4j
@Service
@ConditionalOnSaaSOrUAP
public class RoleServiceImpl implements RoleService {

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    private DeleteCommonDtoMapper deleteCommonDtoMapper;

    @Resource
    private RoleDao roleDao;

    @Autowired
    private RoleMapper roleMapper;

    @Autowired
    private CreateRoleDtoMapper createRoleDtoMapper;

    @Autowired
    private UpdateRoleDtoMapper updateRoleDtoMapper;

    @Autowired
    private ListRoleDtoMapper listRoleDtoMapper;

    @Autowired
    private GetRoleDtoMapper getRoleDtoMapper;

    @Override
    public AppResponse<List<Role>> getUserRoleListInApp(HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        UapUser uapUser = UapUserInfoAPI.getLoginUser(request);
        String userId = null == uapUser ? null : uapUser.getId();
        String accessToken = Oauth2Util.getAccessToken(request);
        List<UapRole> uapRoleList = ClientAuthenticationAPI.getUserRoleListInApp(tenantId, userId, accessToken);
        List<Role> roleList = roleMapper.fromUapRoles(uapRoleList);
        return AppResponse.success(roleList);
    }

    @Override
    public AppResponse<List<Role>> getUserRoleList(HttpServletRequest request) {
        List<UapRole> uapRoleList = UapUserInfoAPI.getUserRoleList(HttpUtils.getRequest());
        List<Role> roleList = roleMapper.fromUapRoles(uapRoleList);
        return AppResponse.success(roleList);
    }

    @Override
    public AppResponse<Role> queryRoleDetail(GetRoleDto dto, HttpServletRequest request) {
        if (StringUtils.isBlank(dto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = UapUserInfoAPI.getTenantId(request);
        com.iflytek.sec.uap.client.core.dto.role.GetRoleDto uapGetRoleDto = getRoleDtoMapper.toUapGetRoleDto(dto);
        UapRole uapRole = ClientManagementAPI.queryRoleDetail(tenantId, uapGetRoleDto);
        Role role = roleMapper.fromUapRole(uapRole);
        return AppResponse.success(role);
    }

    @Override
    public AppResponse<String> addRole(CreateRoleDto createRoleDto, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 校验参数
        if (StringUtils.isBlank(createRoleDto.getName()) || StringUtils.isBlank(createRoleDto.getCode())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色名换或编码不能为空");
        }
        if (createRoleDto.getName().length() >= 100 || createRoleDto.getCode().length() >= 20) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "名称太长，请重新命名");
        }
        String accessToken = Oauth2Util.getAccessToken(request);
        UapApp uapApp = ClientAuthenticationAPI.getUserLoginedAppInfo(accessToken);
        createRoleDto.setAppId(uapApp.getId());
        // 转换为UAP的CreateRoleDto
        com.iflytek.sec.uap.client.core.dto.role.CreateRoleDto uapCreateRoleDto =
                createRoleDtoMapper.toUapCreateRoleDto(createRoleDto);
        ResponseDto<Object> addResult = ClientManagementAPI.addRole(tenantId, uapCreateRoleDto);
        if (addResult.isFlag()) {
            Object data = addResult.getData();
            return AppResponse.success(data != null ? data.toString() : "添加成功");
        }
        log.error("新增角色失败：{}", addResult.getMessage());
        return AppResponse.error(ErrorCodeEnum.E_SERVICE, addResult.getMessage());
    }

    @Override
    public AppResponse<String> updateRole(UpdateRoleDto updateRoleDto, HttpServletRequest request) {
        if (StringUtils.isBlank(updateRoleDto.getId()) || StringUtils.isBlank(updateRoleDto.getName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        // 转换为UAP的UpdateRoleDto
        com.iflytek.sec.uap.client.core.dto.role.UpdateRoleDto uapUpdateRoleDto =
                updateRoleDtoMapper.toUapUpdateRoleDto(updateRoleDto);
        ResponseDto<String> updateResponse =
                ClientManagementAPI.updateRole(UapUserInfoAPI.getTenantId(request), uapUpdateRoleDto);
        if (!updateResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, updateResponse.getMessage());
        }
        return AppResponse.success(updateResponse.getData());
    }

    @Override
    public AppResponse<String> deleteRole(DeleteCommonDto deleteCommonDto, HttpServletRequest request) {
        // 参数校验
        if (StringUtils.isBlank(deleteCommonDto.getId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }

        String roleId = deleteCommonDto.getId();
        // 业务规则：默认角色【未指定】不能删除
        if (roleId.equals("1")) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "默认角色【未指定】不能删除");
        }

        // 获取租户ID
        String tenantId = UapUserInfoAPI.getTenantId(request);

        // 先查询该角色下的用户ID列表
        List<String> userIds = roleDao.getUserIdsByRoleId(databaseName, roleId, tenantId);

        // 如果存在用户，则将该角色下的用户迁移到"未指定"角色
        if (userIds != null && !userIds.isEmpty()) {
            roleDao.migrateUsersToUnspecifiedRole(databaseName, userIds, tenantId);
        }

        // 调用UAP管理客户端删除角色
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        com.iflytek.sec.uap.client.core.dto.DeleteCommonDto uapDeleteCommonDto =
                deleteCommonDtoMapper.toUapDeleteCommonDto(deleteCommonDto);
        ResponseDto<String> deleteResponse = managementClient.deleteRole(uapDeleteCommonDto);
        if (!deleteResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, deleteResponse.getMessage());
        }

        return AppResponse.success(deleteResponse.getData());
    }

    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<Role>> searchRole(
            ListRoleDto listRoleDto, HttpServletRequest request) {
        if (listRoleDto.getRoleName() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        // 转换为UAP的ListRoleDto
        com.iflytek.sec.uap.client.core.dto.role.ListRoleDto uapListRoleDto =
                listRoleDtoMapper.toUapListRoleDto(listRoleDto);
        PageDto<UapRole> uapRolePageDto =
                ClientManagementAPI.queryRolePageList(UapUserInfoAPI.getTenantId(request), uapListRoleDto);
        List<Role> roleList = roleMapper.fromUapRoles(uapRolePageDto.getResult());
        com.iflytek.rpa.auth.core.entity.PageDto<Role> pageDto = new com.iflytek.rpa.auth.core.entity.PageDto<>();
        pageDto.setResult(roleList);
        pageDto.setTotalCount(uapRolePageDto.getTotalCount());
        pageDto.setCurrentPageNo(uapRolePageDto.getCurrentPageNo());
        pageDto.setPageSize(uapRolePageDto.getPageSize());
        return AppResponse.success(pageDto);
    }
}
