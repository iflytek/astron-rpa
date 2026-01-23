package com.iflytek.rpa.auth.sp.uap.service.impl;

import static com.iflytek.rpa.auth.sp.uap.constants.AuthConstant.*;
import static com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant.*;
import static com.iflytek.rpa.auth.utils.RedisUtil.deleteRedisKeysByPrefix;

import cn.hutool.core.collection.CollUtil;
import cn.hutool.core.collection.CollectionUtil;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.AuthService;
import com.iflytek.rpa.auth.core.service.DeptService;
import com.iflytek.rpa.auth.core.service.UserService;
import com.iflytek.rpa.auth.exception.ServiceException;
import com.iflytek.rpa.auth.sp.uap.constants.UAPConstant;
import com.iflytek.rpa.auth.sp.uap.dao.*;
import com.iflytek.rpa.auth.sp.uap.entity.LoginResultDto;
import com.iflytek.rpa.auth.sp.uap.mapper.*;
import com.iflytek.rpa.auth.sp.uap.utils.*;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.sec.uap.base.util.ClientConfigUtil;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.PageDto;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.app.ListAppDto;
import com.iflytek.sec.uap.client.core.dto.app.UapApp;
import com.iflytek.sec.uap.client.core.dto.authentication.TicketDomain;
import com.iflytek.sec.uap.client.core.dto.extand.UapExtendPropertyDto;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.pwd.UpdatePwdDto;
import com.iflytek.sec.uap.client.core.dto.role.RoleBaseDto;
import com.iflytek.sec.uap.client.core.dto.role.UapRole;
import com.iflytek.sec.uap.client.core.dto.tenant.*;
import com.iflytek.sec.uap.client.core.dto.user.*;
import com.iflytek.sec.uap.client.core.dto.user.BindRoleDto;
import com.iflytek.sec.uap.client.core.dto.user.CreateUapUserDto;
import com.iflytek.sec.uap.client.core.dto.user.CreateUserDto;
import com.iflytek.sec.uap.client.core.dto.user.GetUserDto;
import com.iflytek.sec.uap.client.core.dto.user.ListUserByRoleDto;
import com.iflytek.sec.uap.client.core.dto.user.ListUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UpdateUapUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UpdateUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UserExtendDto;
import com.iflytek.sec.uap.client.core.dto.userpool.CreatePoolUserDto;
import com.iflytek.sec.uap.client.core.dto.userpool.CreateUapPoolUserDto;
import com.iflytek.sec.uap.client.core.dto.userpool.UpdatePoolUserDto;
import com.iflytek.sec.uap.client.core.dto.userpool.UpdateUapPoolUserDto;
import com.iflytek.sec.uap.client.util.SessionUtil;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.Base64Utils;

/**
 * @author mjren
 * @date 2025-03-06 15:22
 * @copyright Copyright (c) 2025 mjren
 */
@Slf4j
@Service("userService")
@ConditionalOnSaaSOrUAP
public class UserServiceImpl implements UserService {

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    private DeptService deptService;

    @Autowired
    private DeptDao deptDao;

    @Autowired
    RoleDao roleDao;

    @Autowired
    private UserDao userDao;

    @Autowired
    private TenantDao tenantDao;

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private UserEntitlementDao userEntitlementDao;

    @Autowired
    private CreateUapUserDtoMapper createUapUserDtoMapper;

    @Autowired
    private UpdateUapUserDtoMapper updateUapUserDtoMapper;

    @Autowired
    private GetDeptOrUserDtoMapper getDeptOrUserDtoMapper;

    @Autowired
    private ListUserDtoMapper listUserDtoMapper;

    @Autowired
    private ListUserByRoleDtoMapper listUserByRoleDtoMapper;

    @Autowired
    private GetUserDtoMapper getUserDtoMapper;

    @Autowired
    private UserExtendDtoMapper userExtendDtoMapper;

    @Autowired
    private AuthService authService;

    private Integer smsRetryMax = 3;

    /**
     * 注册
     * @param registerDto 注册信息
     * @param request HTTP请求
     * @return 租户ID
     */
    @Override
    public AppResponse<String> register(RegisterDto registerDto, HttpServletRequest request) {
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        String userId = addPoolUser(buildPoolUser(registerDto), managementClient);
        updateInitialPassword(registerDto);
        String tenantId = createPersonalTenantAndBindRpa(userId, registerDto.getLoginName(), managementClient);

        // 1. 查询"注册角色"的角色ID
        String registerRoleId = roleDao.getRoleIdByName(databaseName, "注册角色");
        if (StringUtils.isBlank(registerRoleId)) {
            log.warn("未找到'注册角色'，使用默认角色ID: 1");
            registerRoleId = "1";
        }

        // 2. 绑定用户到注册角色
        bindRole(userId, registerRoleId, tenantId);

        // 3. 在 t_uap_tenant_role 表中插入租户和角色的关联信息（如果不存在）
        Integer existsCount = roleDao.checkTenantRoleExists(databaseName, tenantId, registerRoleId);
        if (existsCount == null || existsCount == 0) {
            roleDao.insertTenantRole(databaseName, tenantId, registerRoleId);
            log.info("已插入租户角色关联，租户ID: {}, 角色ID: {}", tenantId, registerRoleId);
        } else {
            log.debug("租户角色关联已存在，租户ID: {}, 角色ID: {}", tenantId, registerRoleId);
        }

        return AppResponse.success(tenantId);
    }

    private CreatePoolUserDto buildPoolUser(RegisterDto registerDto) {
        CreatePoolUserDto user = new CreatePoolUserDto();
        user.setLoginName(registerDto.getPhone());
        user.setPhone(registerDto.getPhone());
        user.setName(registerDto.getLoginName());
        return user;
    }

    private void updateInitialPassword(RegisterDto registerDto) {
        if (StringUtils.isEmpty(registerDto.getPassword())) {
            return;
        }
        UpdatePwdDto updatePwdDto = new UpdatePwdDto();
        updatePwdDto.setLoginName(registerDto.getPhone());
        updatePwdDto.setOldPwd(
                Base64Utils.encodeToString(UAPConstant.DEFAULT_INITIAL_PASSWORD.getBytes(StandardCharsets.UTF_8)));
        updatePwdDto.setNewPwd(
                Base64Utils.encodeToString(registerDto.getPassword().getBytes(StandardCharsets.UTF_8)));
        ResponseDto<String> updatePwdResponse = ClientAuthenticationAPI.updateUserPwd(updatePwdDto);
        if (!updatePwdResponse.isFlag()) {
            throw new ServiceException(updatePwdResponse.getMessage());
        }
    }

    public String createPersonalTenantAndBindRpa(String userId, String loginName, ManagementClient managementClient) {
        CreateTenantDto createTenantDto = buildPersonalTenant(userId, loginName);
        UapApp rpaApp = getRpaClientApp(managementClient);
        TenantAppDto tenantAppDto = new TenantAppDto();
        tenantAppDto.setId(rpaApp.getId());
        createTenantDto.setAppList(Collections.singletonList(tenantAppDto));
        ResponseDto<String> tenantResponse = managementClient.addTenant(createTenantDto);
        if (!tenantResponse.isFlag()) {
            throw new ServiceException(tenantResponse.getMessage());
        }
        return tenantResponse.getData();
    }

    private static final String SUFFIX = "的空间";
    private static final int TENANT_NAME_SALT_LENGTH = 6;
    private static final char TENANT_NAME_SEPARATOR = '#';

    private CreateTenantDto buildPersonalTenant(String userId, String loginName) {
        CreateTenantDto createTenantDto = new CreateTenantDto();
        createTenantDto.setTenantCode(UAPConstant.PERSONAL_TENANT_CODE + userId);
        createTenantDto.setName(buildTenantDisplayName(loginName));
        createTenantDto.setStatus(1);
        TenantUserDto tenantUserDto = new TenantUserDto();
        tenantUserDto.setId(userId);
        createTenantDto.setAdminList(Collections.singletonList(tenantUserDto));
        return createTenantDto;
    }

    /**
     * 生成带随机后缀的租户名称，避免 UAP 名称唯一约束冲突。
     */
    private String buildTenantDisplayName(String loginName) {
        String salt =
                RandomStringUtils.randomAlphanumeric(TENANT_NAME_SALT_LENGTH).toLowerCase(Locale.ROOT);
        return loginName + SUFFIX + TENANT_NAME_SEPARATOR + salt;
    }

    private UapApp getRpaClientApp(ManagementClient managementClient) {
        // todo： 由于之前rpa客户端和卓越中心都是在robot项目里，所以在uap配置里共用了一个code，这个code指向了卓越中心。
        // 后续rpa客户端和卓越中心分开后，各自有不同的code，那么下面就需要指向rpa客户端的code，才能更好的做到登录的权限控制。

        ListAppDto listAppDto = new ListAppDto();
        //        listAppDto.setAppName(UAPConstant.RPA_CLIENT_NAME);
        listAppDto.setAppName(UAPConstant.RPA_ADMIN_NAME);
        ResponseDto<PageDto<UapApp>> appPageResponse = managementClient.queryAppPageList(listAppDto);
        if (!appPageResponse.isFlag()) {
            throw new ServiceException(appPageResponse.getMessage());
        }
        PageDto<UapApp> appPage = appPageResponse.getData();
        List<UapApp> appList = appPage == null ? Collections.emptyList() : appPage.getResult();
        return appList.stream()
                .filter(app -> UAPConstant.RPA_ADMIN_NAME.equals(app.getName()))
                .findFirst()
                .orElseThrow(() -> new ServiceException("RPA客户端不存在"));
    }

    // @Override
    // public AppResponse<String> register(RegisterDto registerDto, HttpServletRequest request) {
    //     //todo 入参解密
    //     if (!registerDto.getPassWord().equals(registerDto.getConfirmPassword())) {
    //         return AppResponse.error(ErrorCodeEnum.E_PARAM, "两次输入的密码不一致");
    //     }
    //     //验证码校验
    //     String verifyCode = getVerifyCode(registerDto.getPhone());
    //     if (StringUtils.equals(verifyCode, registerDto.getCode())) {

    //         return doRegister(registerDto, request);
    //     } else {
    //         return AppResponse.error(ErrorCodeEnum.E_PARAM, "验证码错误");
    //     }
    // }

    private AppResponse<String> doRegister(RegisterDto registerDto, HttpServletRequest request) {
        CreatePoolUserDto user = new CreatePoolUserDto();
        BeanUtils.copyProperties(registerDto, user);
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        // 新增资源池用户
        String userId = addPoolUser(user, managementClient);
        // 将默认密码修改为用户传入的密码
        UpdatePwdDto updatePwdDto = new UpdatePwdDto();
        updatePwdDto.setLoginName(registerDto.getLoginName());
        updatePwdDto.setOldPwd(Base64Utils.encodeToString("y3#J3vm!4hJ8k2v".getBytes()));
        updatePwdDto.setNewPwd(
                Base64Utils.encodeToString(registerDto.getPassword().getBytes()));
        ResponseDto<String> updatePwdResponse = ClientAuthenticationAPI.updateUserPwd(updatePwdDto);
        if (!updatePwdResponse.isFlag()) {
            throw new ServiceException(updatePwdResponse.getMessage());
        }
        // 绑定到个人租户
        addToPersonalTenant(userId, managementClient);
        return AppResponse.success("注册成功");
    }

    public String getVerifyCode(String phone) {
        String smsPrefix = SMS_REGISTER_PREFIX;
        String retryNumPrefix = SMS_REGISTER_RETRY_NUM;
        String smsCode = SMS_REGISTER_CODE;
        Object retryNumStr = RedisUtils.get(smsPrefix + ":" + phone + ":" + retryNumPrefix);
        if (retryNumStr != null) {
            int retryTimes = (int) retryNumStr;
            // 限制重试次数，防止撞库攻击,导致不用发验证码也能大量注册
            if (retryTimes >= smsRetryMax) {
                RedisUtils.del(smsPrefix + ":" + phone + ":" + retryNumPrefix);
                RedisUtils.del(smsPrefix + ":" + phone + ":" + smsCode);
                return null;
            }
        }
        RedisUtils.incr(smsPrefix + ":" + phone + ":" + retryNumPrefix, 1);
        return String.valueOf(RedisUtils.get(smsPrefix + ":" + phone + ":" + smsCode));
    }

    /**
     * 删除员工
     * @param userDto 删除员工DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> deleteUser(UserDeleteDto userDto, HttpServletRequest request) {
        List<String> userIdList = userDto.getUserIdList();
        if (CollectionUtil.isEmpty(userIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        for (String userId : userIdList) {
            com.iflytek.sec.uap.client.core.dto.DeleteCommonDto deleteCommonDto =
                    new com.iflytek.sec.uap.client.core.dto.DeleteCommonDto();
            deleteCommonDto.setId(userId);
            ResponseDto<String> deleteResponse = managementClient.deleteUser(deleteCommonDto);
            if (!deleteResponse.isFlag()) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, deleteResponse.getMessage());
            }
        }
        // 部门用户缓存
        deleteRedisKeysByPrefix(REDIS_KEY_DEPT_USER_PREFIX);
        // 租户用户缓存
        deleteRedisKeysByPrefix(REDIS_KEY_TENANT_USER_PREFIX);
        return AppResponse.success("操作成功");
    }

    /**
     * 启用/禁用员工
     * 变更用户基础信息只能通过资源池相关接口，普通用户接口无权限编辑资源池用户基本信息
     * @param userDto 启用/禁用DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> enableUser(UserEnableDto userDto, HttpServletRequest request) {
        /*
        变更用户基础信息只能通过资源池相关接口，普通用户接口无权限编辑资源池用户基本信息
         */
        List<com.iflytek.rpa.auth.core.entity.UpdateUserDto> updateUserDtoList = userDto.getUserList();
        Integer status = userDto.getStatus();
        if (CollectionUtil.isEmpty(updateUserDtoList) || status == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        if (!status.equals(0) && !status.equals(1)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        // ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        for (com.iflytek.rpa.auth.core.entity.UpdateUserDto updateUserDto : updateUserDtoList) {
            if (updateUserDto == null || StringUtils.isBlank(updateUserDto.getId())) {
                continue;
            }
            String tenantUserId =
                    tenantDao.getTenantUserId(databaseName, updateUserDto.getId(), UapUserInfoAPI.getTenantId(request));
            Integer i = tenantDao.enableTenantUser(databaseName, tenantUserId, status);
            if (i == null || i == 0) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "操作失败");
            }
            /*            UpdateUapPoolUserDto updateUapPoolUserDto = new UpdateUapPoolUserDto();
            UpdatePoolUserDto poolUserDto = new UpdatePoolUserDto();
            poolUserDto.setId(updateUserDto.getId());
            poolUserDto.setLoginName(updateUserDto.getLoginName());
            poolUserDto.setStatus(status);
            updateUapPoolUserDto.setUser(poolUserDto);
            ResponseDto<String> updateUserResponse = managementClient.updatePoolUser(updateUapPoolUserDto);

            if (!updateUserResponse.isFlag()) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, updateUserResponse.getMessage());
            }*/
        }
        return AppResponse.success("操作成功");
    }

    private String addPoolUser(CreatePoolUserDto user, ManagementClient managementClient) {

        CreateUapPoolUserDto createUapPoolUserDto = new CreateUapPoolUserDto();
        createUapPoolUserDto.setUser(user);
        ResponseDto<String> addPoolUserResponse = managementClient.addPoolUser(createUapPoolUserDto);
        if (!addPoolUserResponse.isFlag()) {
            throw new ServiceException(addPoolUserResponse.getMessage());
        }
        return addPoolUserResponse.getData();
    }

    private void addToPersonalTenant(String userId, ManagementClient managementClient) {
        // 查找个人租户
        ListTenantDto listTenantDto = new ListTenantDto();
        listTenantDto.setName(PERSONAL_TENANT_NAME);
        ResponseDto<PageDto<UapTenant>> tenantPageResponse = managementClient.queryTenantPageList(listTenantDto);
        if (!tenantPageResponse.isFlag()) {
            throw new ServiceException(tenantPageResponse.getMessage());
        }
        List<UapTenant> tenantList = tenantPageResponse.getData().getResult();
        UapTenant personalTenant = null;
        for (UapTenant tenant : tenantList) {
            if (null == tenant) {
                continue;
            }
            if (PERSONAL_TENANT_NAME.equals(tenant.getName())) {
                personalTenant = tenant;
            }
        }
        if (null == personalTenant) {
            // todo 删除资源池用户
            throw new ServiceException("未找到个人租户");
        }
        // 绑定到个人租户
        TenantBindUserDto tenantBindUserDto = new TenantBindUserDto();
        tenantBindUserDto.setTenantId(personalTenant.getId());
        tenantBindUserDto.setUserIds(Collections.singletonList(userId));
        ResponseDto<String> bindResponse = managementClient.bindTenantUser(tenantBindUserDto);
        if (!bindResponse.isFlag()) {
            throw new ServiceException(bindResponse.getMessage());
        }
    }

    /**
     * 按名称模糊搜索所有员工或部门
     * @param name 名称
     * @param request HTTP请求
     * @return 部门或用户信息
     */
    @Override
    public AppResponse<GetDeptOrUserDto> searchDeptOrUser(String name, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);

        List<UapUser> uapUsers = userDao.queryUapUserByName(name, tenantId, databaseName);
        List<UapOrg> deptList = deptDao.queryUapOrgByName(name, tenantId, databaseName);

        GetDeptOrUserDto result = getDeptOrUserDtoMapper.toCoreGetDeptOrUserDto(uapUsers, deptList);

        return AppResponse.success(result);
    }

    /**
     * 编辑用户信息，资源池用户只允许修改所属机构和角色，基本信息不允许修改
     *
     * @param updateUapUserDto
     * @param request
     * @return
     */
    @Override
    public AppResponse<String> editUser(
            com.iflytek.rpa.auth.core.entity.UpdateUapUserDto updateUapUserDto, HttpServletRequest request) {
        // core实体类转uap实体类
        UpdateUapUserDto uapUpdateUapUserDto = updateUapUserDtoMapper.toUapUpdateUapUserDto(updateUapUserDto);
        // 1. 参数校验
        UpdateUserDto userInfo = uapUpdateUapUserDto.getUser();
        if (isInvalidUserInfo(userInfo)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }

        // 2. 提取并处理角色信息
        String roleId = extractAndRemoveRoleId(uapUpdateUapUserDto);

        String userId = userInfo.getId();

        // 3. 获取用户当前角色
        String oldRoleId = getCurrentUserRoleId(userId, userInfo.getLoginName(), request);

        // 4. 处理角色绑定/解绑
        handleRoleBinding(userId, roleId, oldRoleId, request);

        // 5. 更新用户基本信息
        return updateUserBasicInfo(uapUpdateUapUserDto, request);
    }

    // 辅助方法：校验用户信息
    private boolean isInvalidUserInfo(UpdateUserDto userInfo) {
        return userInfo == null || userInfo.getLoginName() == null || userInfo.getStatus() == null;
    }

    // 从扩展属性中提取并移除角色ID
    private String extractAndRemoveRoleId(UpdateUapUserDto updateUapUserDto) {
        List<UapExtendPropertyDto> extands = updateUapUserDto.getExtands();

        String roleId = null;
        List<UapExtendPropertyDto> toRemove = new ArrayList<>();
        for (UapExtendPropertyDto extendInfo : extands) {
            if (extendInfo.getId().equals("roleId")) {
                roleId = extendInfo.getValue();
                toRemove.add(extendInfo);
            }
        }
        extands.removeAll(toRemove);
        updateUapUserDto.setExtands(extands);
        return roleId;
    }

    // 获取用户当前角色ID
    private String getCurrentUserRoleId(String userId, String loginName, HttpServletRequest request) {
        GetUserDto getUserDto = new GetUserDto();
        getUserDto.setUserId(userId);
        getUserDto.setLoginName(loginName);

        List<UapRole> roleList = ClientManagementAPI.queryRoleListByUserId(UapUserInfoAPI.getTenantId(request), userId);

        if (roleList.size() > 1) {
            throw new ServiceException("用户存在多个绑定角色");
        }

        return roleList.get(0) != null ? roleList.get(0).getId() : null;
    }

    // 处理角色绑定逻辑
    private void handleRoleBinding(String userId, String newRoleId, String oldRoleId, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 情况1: 新角色ID为空且旧角色ID不为空 - 解绑旧角色
        if (StringUtils.isBlank(newRoleId) && StringUtils.isNotBlank(oldRoleId)) {
            unbindRole(userId, oldRoleId, tenantId);
        }
        // 填充角色【未指定】
        if (StringUtils.isEmpty(newRoleId)) {
            newRoleId = "1";
        }
        // 情况2: 新角色ID不为空且与旧角色不同 - 先解绑旧角色再绑定新角色
        if (StringUtils.isNotBlank(newRoleId) && !newRoleId.equals(oldRoleId)) {
            if (StringUtils.isNotBlank(oldRoleId)) {
                unbindRole(userId, oldRoleId, tenantId);
            }
            bindRole(userId, newRoleId, tenantId);
        }
    }

    // 解绑角色
    private void unbindRole(String userId, String roleId, String tenantId) {
        BindRoleDto bindRoleDto = createBindRoleDto(userId, roleId);
        ResponseDto<Object> response = ClientManagementAPI.unbindUserRole(tenantId, bindRoleDto);
        if (!response.isFlag()) {
            throw new ServiceException(response.getMessage());
        }
    }

    // 绑定角色
    private void bindRole(String userId, String roleId, String tenantId) {
        BindRoleDto bindRoleDto = createBindRoleDto(userId, roleId);
        ResponseDto<Object> response = ClientManagementAPI.bindUserRole(tenantId, bindRoleDto);
        if (!response.isFlag()) {
            throw new ServiceException(response.getMessage());
        }
    }

    // 创建角色绑定DTO
    private BindRoleDto createBindRoleDto(String userId, String roleId) {
        BindRoleDto bindRoleDto = new BindRoleDto();
        bindRoleDto.setUserId(userId);
        bindRoleDto.setRoleIdList(Collections.singletonList(roleId));
        return bindRoleDto;
    }

    /**
     * 当用户没有角色时，分配注册角色并重新获取角色列表
     *
     * @param tenantId 租户ID
     * @param userId 用户ID
     * @param accessToken 访问令牌
     * @param loginName 登录名（用于日志）
     * @return 角色列表，如果分配失败则返回空列表
     */
    private List<UapRole> assignRegisterRoleIfNeeded(
            String tenantId, String userId, String accessToken, String loginName) {
        try {
            // 查询"注册角色"的角色ID
            String registerRoleId = roleDao.getRoleIdByName(databaseName, "注册角色");
            if (StringUtils.isBlank(registerRoleId)) {
                log.warn("未找到'注册角色'，使用默认角色ID: 1");
                registerRoleId = "1";
            }

            // 绑定用户到注册角色
            bindRole(userId, registerRoleId, tenantId);
            log.info("已为用户 {} 绑定注册角色，角色ID: {}", loginName, registerRoleId);

            // 确保租户角色关联存在
            Integer existsCount = roleDao.checkTenantRoleExists(databaseName, tenantId, registerRoleId);
            if (existsCount == null || existsCount == 0) {
                roleDao.insertTenantRole(databaseName, tenantId, registerRoleId);
                log.info("已插入租户角色关联，租户ID: {}, 角色ID: {}", tenantId, registerRoleId);
            }

            // 重新获取角色列表
            List<UapRole> roleList = ClientAuthenticationAPI.getUserRoleListInApp(tenantId, userId, accessToken);
            if (CollectionUtil.isEmpty(roleList)) {
                log.warn("绑定注册角色后，重新获取角色列表仍为空");
            }
            return roleList != null ? roleList : Collections.emptyList();
        } catch (Exception e) {
            log.error("为用户 {} 绑定注册角色失败", loginName, e);
            return Collections.emptyList();
        }
    }

    // 更新用户基本信息
    private AppResponse<String> updateUserBasicInfo(UpdateUapUserDto updateUapUserDto, HttpServletRequest request) {
        UpdateUserDto user = updateUapUserDto.getUser();
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        // 编辑接口，更新资源池用户基本信息，如邮箱，姓名等，不包括部门和角色
        UpdateUapPoolUserDto updateUapPoolUserDto = new UpdateUapPoolUserDto();
        UpdatePoolUserDto poolUser = new UpdatePoolUserDto();
        BeanUtils.copyProperties(user, poolUser);
        updateUapPoolUserDto.setUser(poolUser);
        ResponseDto<String> updateUserResponse = managementClient.updatePoolUser(updateUapPoolUserDto);
        if (!updateUserResponse.isFlag()) {
            return AppResponse.error(updateUserResponse.getMessage());
        }
        if (StringUtils.isBlank(user.getOrgId())) {
            return AppResponse.success("操作成功，未绑定部门");
        }
        // 更新部门
        user.setUserType(3);
        UapUser userInfo = UserUtils.getUserInfoById(user.getId());
        if (null == userInfo) {
            return AppResponse.error("为查询到添加的用户信息");
        }
        // 必须设置email,可以是空字符串,否则报错：租户空间内无法编辑资源池用户
        user.setEmail(userInfo.getEmail());
        user.setIdNumber(userInfo.getIdNumber());
        user.setRemark(userInfo.getRemark());
        user.setAddress(userInfo.getAddress());
        ResponseDto<String> response = managementClient.updateUser(updateUapUserDto);
        if (!response.isFlag()) {
            throw new ServiceException(response.getMessage());
        }

        // 部门用户缓存
        deleteRedisKeysByPrefix(REDIS_KEY_DEPT_USER_PREFIX);
        // 租户用户缓存
        deleteRedisKeysByPrefix(REDIS_KEY_TENANT_USER_PREFIX);

        return AppResponse.success("操作成功");

        // todo 任一步骤失败，回滚之间的操作
    }

    /**
     * 添加资源池用户
     *
     * @param createUapUserDto
     * @param request
     * @return
     */
    @Override
    public AppResponse<String> addUser(
            com.iflytek.rpa.auth.core.entity.CreateUapUserDto createUapUserDto, HttpServletRequest request) {
        CreateUapUserDto uapCreateUapUserDto = createUapUserDtoMapper.toUapCreateUapUserDto(createUapUserDto);
        // 1. 参数校验
        validateCreateUserDto(uapCreateUapUserDto);

        // 2. 处理默认部门分配
        handleDefaultOrganization(uapCreateUapUserDto, request);

        // 3. 创建资源池用户
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        String userId = createPoolUser(uapCreateUapUserDto.getUser(), managementClient);
        if (userId == null) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "创建用户失败");
        }

        // 4. 企业租户绑定资源池用户
        bindTenantUser(userId, request);

        // 5. 用户绑定部门和角色
        bindOrganizationAndRole(userId, uapCreateUapUserDto, request);

        // 绑定个人空间
        addToPersonalTenant(userId, managementClient);

        return AppResponse.success("操作成功");
        // todo 任一步骤失败，回滚之前的操作
    }

    private void bindTenantUser(String userId, HttpServletRequest request) {
        TenantBindUserDto tenantBindUserDto = new TenantBindUserDto();
        tenantBindUserDto.setTenantId(UapUserInfoAPI.getTenantId(request));
        tenantBindUserDto.setUserIds(Collections.singletonList(userId));
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        ResponseDto<String> bindResponse = managementClient.bindTenantUser(tenantBindUserDto);
        if (!bindResponse.isFlag()) {
            throw new ServiceException(bindResponse.getMessage());
        }
    }

    // 验证创建用户参数
    private void validateCreateUserDto(CreateUapUserDto createUapUserDto) {
        CreateUserDto userDto = createUapUserDto.getUser();
        if (userDto == null || userDto.getLoginName() == null) {
            throw new ServiceException("用户名不能为空");
        }
    }

    // 处理默认部门分配
    private void handleDefaultOrganization(CreateUapUserDto createUapUserDto, HttpServletRequest request) {
        CreateUserDto userDto = createUapUserDto.getUser();

        String tenantId = UapUserInfoAPI.getTenantId(request);
        if (StringUtils.isNotBlank(userDto.getOrgId())) {
            return;
        }
        String unGroupOrgId = findUnassignedOrganization(tenantId, request);

        userDto.setOrgId(unGroupOrgId);
        createUapUserDto.setUser(userDto);
    }

    // 查找未分组部门
    private String findUnassignedOrganization(String tenantId, HttpServletRequest request) {
        OrgListDto orgListDto = new OrgListDto();
        orgListDto.setOrgName("未分组");

        ResponseDto<PageDto<UapOrg>> orgPageList =
                UapManagementClientUtil.queryOrgPageList(tenantId, orgListDto, request);

        if (!orgPageList.isFlag()) {
            throw new ServiceException(orgPageList.getMessage());
        }

        if (orgPageList.getData() == null
                || CollectionUtil.isEmpty(orgPageList.getData().getResult())) {
            throw new ServiceException("未找到未分组部门信息");
        }

        String unGroupOrgId = findUnGroupOrgId(orgPageList.getData().getResult());
        if (unGroupOrgId == null) {
            throw new ServiceException("未找到未分组部门信息");
        }

        return unGroupOrgId;
    }

    // 辅助方法：查找未分组部门ID
    private String findUnGroupOrgId(List<UapOrg> orgList) {
        return orgList.stream()
                .filter(org -> org != null && "未分组".equals(org.getName()))
                .findFirst()
                .map(UapOrg::getId)
                .orElse(null);
    }

    // 创建资源池用户
    private String createPoolUser(CreateUserDto createUserDto, ManagementClient managementClient) {
        CreatePoolUserDto createPoolUserDto = new CreatePoolUserDto();
        BeanUtils.copyProperties(createUserDto, createPoolUserDto);
        return addPoolUser(createPoolUserDto, managementClient);
    }

    // 绑定部门和角色
    private void bindOrganizationAndRole(String userId, CreateUapUserDto createUapUserDto, HttpServletRequest request) {
        UpdateUapUserDto updateUapUserDto = new UpdateUapUserDto();
        UpdateUserDto user = new UpdateUserDto();

        user.setId(userId);
        user.setName(createUapUserDto.getUser().getName());
        // 类型为资源池用户
        user.setUserType(3);
        user.setLoginName(createUapUserDto.getUser().getLoginName());
        user.setPhone(createUapUserDto.getUser().getPhone());
        user.setOrgId(createUapUserDto.getUser().getOrgId());
        user.setEmail(createUapUserDto.getUser().getEmail());

        updateUapUserDto.setUser(user);
        updateUapUserDto.setExtands(createUapUserDto.getExtands());

        // uap转core实体类
        com.iflytek.rpa.auth.core.entity.UpdateUapUserDto coreUpdateUapUserDto =
                updateUapUserDtoMapper.fromUapUpdateUapUserDto(updateUapUserDto);
        editUser(coreUpdateUapUserDto, request);
    }

    /**
     * 分页查询当前机构的用户
     * @param listUserDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<DeptUserDto>> queryUserListByOrgId(
            com.iflytek.rpa.auth.core.entity.ListUserDto listUserDto, HttpServletRequest request) { //
        // core 映射到 uap 实体
        ListUserDto uapListUserDto = listUserDtoMapper.toUapListUserDto(listUserDto);

        if (StringUtils.isBlank(uapListUserDto.getOrgId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少部门id");
        }
        if (uapListUserDto.getPageNum() == null || uapListUserDto.getPageSize() == null) {
            uapListUserDto.setPageNum(1);
            uapListUserDto.setPageSize(100);
        }
        // 查全部状态
        uapListUserDto.setStatus(null);
        PageDto<UserExtendDto> userInfoPage =
                ClientManagementAPI.queryUserDetailPageList(UapUserInfoAPI.getTenantId(request), uapListUserDto);
        List<UserExtendDto> userExtendDtoList = userInfoPage.getResult();
        List<DeptUserDto> deptUserDtoList = new ArrayList<>();
        for (UserExtendDto userExtendDto : userExtendDtoList) {
            DeptUserDto deptUserDto = new DeptUserDto();
            UapUser user = userExtendDto.getUser();
            Integer tenantUserStatus =
                    tenantDao.getTenantUserStatus(databaseName, user.getId(), UapUserInfoAPI.getTenantId(request));
            user.setStatus(tenantUserStatus);
            BeanUtils.copyProperties(user, deptUserDto);
            List<RoleBaseDto> roleList = userExtendDto.getRoles();
            if (!CollUtil.isEmpty(roleList)) {
                if (roleList.size() > 1) {
                    //                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户存在多个绑定角色");
                }
                RoleBaseDto role = roleList.get(0);
                if (null != role) {
                    deptUserDto.setRoleId(role.getId());
                    deptUserDto.setRoleName(role.getName());
                }
            }
            deptUserDtoList.add(deptUserDto);
        }
        com.iflytek.rpa.auth.core.entity.PageDto<DeptUserDto> deptUserPage =
                new com.iflytek.rpa.auth.core.entity.PageDto<>();
        deptUserPage.setResult(deptUserDtoList);
        deptUserPage.setPageSize(userInfoPage.getPageSize());
        deptUserPage.setCurrentPageNo(userInfoPage.getCurrentPageNo());
        deptUserPage.setTotalCount(userInfoPage.getTotalCount());
        return AppResponse.success(deptUserPage);
    }

    /**
     * 角色管理-根据部门id查询部门下的人员和子部门
     * @param id 部门ID
     * @param request HTTP请求
     * @return 部门用户列表
     */
    @Override
    public AppResponse<List<CurrentDeptUserDto>> queryUserAndDept(String id, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);

        // 如果id为0，则查找卓越中心的id
        if (TOP_ORG_ID.equals(id)) {
            UapUser uapUser = UapUserInfoAPI.getLoginUser(request);
            String loginName = null == uapUser ? null : uapUser.getLoginName();
            String firstLevelOrgId = deptDao.queryFirstLevelOrgIdByLoginName(loginName, tenantId, databaseName);
            if (StringUtils.isBlank(firstLevelOrgId)) {
                return AppResponse.success(new ArrayList<>());
            }
            id = firstLevelOrgId;
        }

        List<CurrentDeptUserDto> result = new ArrayList<>();

        // 查询部门下的人
        List<UserVo> userList = deptDao.queryUserListByDeptId(null, id, tenantId, databaseName);

        // 查询这些用户中哪些有角色
        List<String> userIdList = new ArrayList<>();
        if (!CollectionUtil.isEmpty(userList)) {
            for (UserVo userVo : userList) {
                if (userVo != null && userVo.getUserId() != null) {
                    userIdList.add(userVo.getUserId());
                }
            }
        }

        // 获取有角色的用户ID和角色名称集合
        List<UserRoleDto> usersWithRoles = new ArrayList<>();
        if (!CollectionUtil.isEmpty(userIdList)) {
            usersWithRoles = deptDao.queryUserIdsWithRoles(userIdList, tenantId, databaseName);
            usersWithRoles.removeIf(Objects::isNull);
        }

        Map<String, String> userIdMapRoleName = usersWithRoles.stream()
                .filter(Objects::nonNull)
                .collect(Collectors.toMap(UserRoleDto::getUserId, UserRoleDto::getRoleName, (v1, v2) -> v1));

        if (!CollectionUtil.isEmpty(userList)) {
            // 设置状态
            for (UserVo userVo : userList) {
                if (null == userVo) {
                    continue;
                }
                CurrentDeptUserDto currentDeptUserDto = new CurrentDeptUserDto();
                currentDeptUserDto.setId(userVo.getUserId());
                currentDeptUserDto.setName(userVo.getUserName() + "(" + userVo.getUserPhone() + ")");
                currentDeptUserDto.setType(TYPE_USER);

                String roleName = null;
                boolean hasRole = false;
                if (userIdMapRoleName.containsKey(userVo.getUserId())) {
                    String roleN = userIdMapRoleName.get(userVo.getUserId());
                    if (roleN.trim().equals("未指定")) {
                        roleName = roleN;
                    } else {
                        hasRole = true;
                        roleName = roleN;
                    }
                }
                currentDeptUserDto.setStatus(hasRole);
                currentDeptUserDto.setRoleName(roleName);
                result.add(currentDeptUserDto);
            }
        }

        // 查询部门下的子级部门
        List<UserVo> childOrgList = deptDao.queryChildOrgsByParentOrgId(id, tenantId, databaseName);
        if (!CollectionUtil.isEmpty(childOrgList)) {
            childOrgList.removeIf(Objects::isNull);
            for (UserVo childOrg : childOrgList) {
                CurrentDeptUserDto currentDeptUserDto = new CurrentDeptUserDto();
                currentDeptUserDto.setId(childOrg.getUserId());
                currentDeptUserDto.setName(childOrg.getUserName());
                currentDeptUserDto.setType(TYPE_DEPT);
                result.add(currentDeptUserDto);
            }
        }
        return AppResponse.success(result);
    }

    /**
     * 角色管理-根据名字或手机号模糊查询员工
     * @param keyWord 关键字
     * @param request HTTP请求
     * @return 用户列表
     */
    @Override
    public AppResponse<List<CurrentDeptUserDto>> searchUserWithStatus(String keyWord, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 查全部状态
        ListUserDto listUserDto = new ListUserDto();
        listUserDto.setPageNum(1);
        listUserDto.setPageSize(100);
        listUserDto.setName(keyWord);
        listUserDto.setStatus(null);
        PageDto<UserExtendDto> userInfoPageByName = ClientManagementAPI.queryUserDetailPageList(tenantId, listUserDto);
        List<UserExtendDto> userExtendDtoListByName = userInfoPageByName.getResult();
        listUserDto.setName(null);
        listUserDto.setPhone(keyWord);
        PageDto<UserExtendDto> userInfoPageByPhone = ClientManagementAPI.queryUserDetailPageList(tenantId, listUserDto);
        List<UserExtendDto> userExtendDtoListByPhone = userInfoPageByPhone.getResult();
        List<UserExtendDto> userExtendList = new ArrayList<>();
        if (!CollUtil.isEmpty(userExtendDtoListByName)) {
            userExtendList.addAll(userExtendDtoListByName);
        }
        if (!CollUtil.isEmpty(userExtendDtoListByPhone)) {
            userExtendList.addAll(userExtendDtoListByPhone);
        }
        if (CollUtil.isEmpty(userExtendList)) {
            return AppResponse.success(new ArrayList<>());
        }
        List<CurrentDeptUserDto> userList = new ArrayList<>();
        for (UserExtendDto userExtendDto : userExtendList) {
            CurrentDeptUserDto currentDeptUserDto = new CurrentDeptUserDto();
            UapUser user = userExtendDto.getUser();
            currentDeptUserDto.setId(user.getId());
            currentDeptUserDto.setName(user.getName() + "(" + user.getPhone() + ")");
            currentDeptUserDto.setType(TYPE_USER);
            List<RoleBaseDto> roleList = userExtendDto.getRoles();
            if (!CollUtil.isEmpty(roleList)) {
                if (roleList.size() > 1) {
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户存在多个绑定角色");
                }
                RoleBaseDto role = roleList.get(0);
                currentDeptUserDto.setStatus(null != role);
            }
            userList.add(currentDeptUserDto);
        }
        return AppResponse.success(userList);
    }

    /**
     * 角色管理-添加成员
     * @param bindUserListDto 绑定用户列表DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    @Transactional
    public AppResponse<String> bindUserListRole(BindUserListDto bindUserListDto, HttpServletRequest request) {
        if (StringUtils.isBlank(bindUserListDto.getRoleId()) || CollUtil.isEmpty(bindUserListDto.getUserIds())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 新查询 userIds 所有 绑定 角色【未指定】 的 id
        List<String> userIds = bindUserListDto.getUserIds();
        String roleId = bindUserListDto.getRoleId();
        if (!roleId.equals("1")) {
            List<String> ids = roleDao.getBindUnspecifiedRoleIds(userIds, tenantId, databaseName);
            if (!ids.isEmpty()) {
                roleDao.batchDeleteUnspecifiedRoleBind(ids, databaseName);
            }
        }
        userIds.parallelStream().forEach(userId -> {
            BindRoleDto bindRoleDto = new BindRoleDto();
            bindRoleDto.setUserId(userId);
            bindRoleDto.setRoleIdList(Collections.singletonList(bindUserListDto.getRoleId()));
            ResponseDto<Object> bindRoleResponse = ClientManagementAPI.bindUserRole(tenantId, bindRoleDto);
            if (!bindRoleResponse.isFlag()) {
                throw new ServiceException(bindRoleResponse.getMessage());
            }
        });
        return AppResponse.success("添加成功");
    }

    /**
     * 人员解绑角色
     * @param bindRoleDto 绑定角色DTO
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> unbindRole(
            com.iflytek.rpa.auth.core.entity.BindRoleDto bindRoleDto, HttpServletRequest request) {

        if (StringUtils.isBlank(bindRoleDto.getUserId()) || CollectionUtil.isEmpty(bindRoleDto.getRoleIdList())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String userId = bindRoleDto.getUserId();
        // 如果存在用户，则将该角色下的用户迁移到"未指定"角色
        if (userId != null && !userId.isEmpty()) {
            List<String> userIds = new ArrayList<>();
            userIds.add(userId);
            String tenantId = UapUserInfoAPI.getTenantId(request);
            roleDao.migrateUsersToUnspecifiedRole(databaseName, userIds, tenantId);
        }
        return AppResponse.success("解绑成功");
    }

    /**
     * 分页获取角色绑定的用户列表，可根据登录名或姓名模糊查询
     * @param listUserByRoleDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<User>> queryBindListByRole(
            com.iflytek.rpa.auth.core.entity.ListUserByRoleDto listUserByRoleDto, HttpServletRequest request) {
        // core映射到uap实体
        ListUserByRoleDto uapListUserByRoleDto = listUserByRoleDtoMapper.toUapListUserByRoleDto(listUserByRoleDto);
        if (uapListUserByRoleDto == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "请求参数不能为空");
        }
        if (StringUtils.isBlank(uapListUserByRoleDto.getRoleId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少角色id");
        }
        Integer pageNum = uapListUserByRoleDto.getPageNum();
        if (pageNum == null || pageNum < 1) {
            pageNum = 1;
        }
        Integer pageSize = uapListUserByRoleDto.getPageSize();
        if (pageSize == null || pageSize < 1) {
            pageSize = 10;
        }
        if (pageSize > 1000) {
            pageSize = 1000;
        }
        IPage pageConfig = new Page<>(pageNum, pageSize, true);
        IPage<String> idPage = userDao.queryUserIdsByRole(pageConfig, uapListUserByRoleDto, databaseName);

        long total = idPage.getTotal();
        long current = idPage.getCurrent();
        long size = idPage.getSize();
        List<String> ids = idPage.getRecords();
        if (CollectionUtil.isEmpty(ids)) {
            com.iflytek.rpa.auth.core.entity.PageDto<User> emptyPageDto =
                    new com.iflytek.rpa.auth.core.entity.PageDto<>();
            emptyPageDto.setCurrentPageNo((int) current);
            emptyPageDto.setPageSize((int) size);
            emptyPageDto.setTotalCount((int) total);
            emptyPageDto.setResult(new ArrayList<>());
            return AppResponse.success(emptyPageDto);
        }
        String tenantId = UapUserInfoAPI.getTenantId(request);
        List<UapUser> list = userDao.queryUapUserByIds(ids, databaseName, tenantId);
        List<User> userList = userMapper.fromUapUsers(list);

        com.iflytek.rpa.auth.core.entity.PageDto<User> pageDto = new com.iflytek.rpa.auth.core.entity.PageDto<>();
        pageDto.setCurrentPageNo((int) current);
        pageDto.setPageSize((int) size);
        pageDto.setTotalCount((int) total);
        pageDto.setResult(userList);
        return AppResponse.success(pageDto);
    }

    public AppResponse<UapUser> loginNoPasswordByPhone(String phone, String tenantId, HttpServletRequest request) {
        if (StringUtils.isBlank(phone)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "手机号不能为空");
        }
        if (StringUtils.isBlank(tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
        }
        try {
            ListUserDto listUserDto = new ListUserDto();
            listUserDto.setPhone(phone);
            listUserDto.setPageSize(1);
            PageDto<UapUser> userPage = ClientManagementAPI.queryUserPageList(tenantId, listUserDto);
            if (userPage == null || CollectionUtil.isEmpty(userPage.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到手机号对应的用户");
            }
            UapUser targetUser = userPage.getResult().get(0);
            if (targetUser == null || StringUtils.isBlank(targetUser.getLoginName())) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "手机号未绑定登录账号");
            }
            return loginNoPassword(targetUser.getLoginName(), tenantId, request);
        } catch (Exception e) {
            log.error("登录失败, phone: {}, tenantId: {}", phone, tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "登录失败: " + e.getMessage());
        }
    }

    /**
     * 无密码登录（仅通过账号登录）
     *
     * @param loginName 登录账号
     * @param tenantId 租户ID（可选）
     * @param request HTTP请求
     * @return 登录结果，包含用户信息
     */
    public AppResponse<UapUser> loginNoPassword(String loginName, String tenantId, HttpServletRequest request) {
        try {
            // 1. 调用 ClientAuthenticationAPIExt.loginUapByAccount 获取 ticket
            log.info("开始无密码登录，账号: {}, 租户ID: {}", loginName, tenantId);
            LoginResultDto loginResult = ClientAuthenticationAPIExt.loginUapByAccount(loginName, tenantId);

            if (loginResult == null || StringUtils.isBlank(loginResult.getTicket())) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取登录凭证失败");
            }

            String ticket = loginResult.getTicket();
            String service = ClientConfigUtil.instance().getCasClientContext();

            // 2. 调用 ClientAuthenticationAPI.validateTicket 验证 ticket
            // 注意：validateTicket 内部会自动处理 token 的保存到 Redis（UAP框架自动完成）
            ResponseDto<TicketDomain> validateResponse = ClientAuthenticationAPI.validateTicket(ticket, service);

            if (validateResponse == null || !validateResponse.isFlag()) {
                String errorMsg = validateResponse != null ? validateResponse.getMessage() : "验证登录凭证失败";
                log.error("验证 ticket 失败: {}", errorMsg);
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, errorMsg);
            }

            // 3. 从 validateTicket 的返回结果中获取 UapUser
            TicketDomain ticketDomain = validateResponse.getData();
            if (ticketDomain == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "验证结果为空");
            }

            UapUser uapUser = ticketDomain.getUapUser();
            if (uapUser == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "无法从验证结果中获取用户信息");
            }

            // 4. 将用户信息保存到 session
            javax.servlet.http.HttpSession session = request.getSession(true);
            SessionUtil.getInstance().saveUser(session, uapUser);
            SessionUtil.getInstance().saveTenantId(session, tenantId);

            // 5. 从 TicketDomain 中提取并保存 accessToken 和 refreshToken 到 Redis
            // 使用与 UAP 兼容的序列化方式（JdkSerializationRedisSerializer）
            String accessToken = ticketDomain.getAccessToken();
            String refreshToken = ticketDomain.getRefreshToken();

            // 通过accessToken获取租户信息
            UapTenant uapTenant = ClientAuthenticationAPI.getTenantInfo(tenantId, accessToken);
            SessionUtil.getInstance().saveTenant(session, uapTenant);

            // 调用 ClientAuthenticationAPI.getUserRoleListInApp 获取用户角色列表
            List<UapRole> roleList =
                    ClientAuthenticationAPI.getUserRoleListInApp(tenantId, uapUser.getId(), accessToken);
            if (CollectionUtil.isEmpty(roleList)) {
                log.warn("用户 {} 在租户 {} 中没有角色，尝试分配注册角色", uapUser.getLoginName(), tenantId);
                roleList = assignRegisterRoleIfNeeded(tenantId, uapUser.getId(), accessToken, uapUser.getLoginName());
            }

            // 保存角色列表到 session
            if (!CollectionUtil.isEmpty(roleList)) {
                SessionUtil.getInstance().saveUserRole(session, roleList);
            }

            LocalDateTime expTime = ticketDomain.getExpTime();
            Long cacheSecond = 0L;
            if (null == expTime) {
                cacheSecond = 7200L;
            } else {
                // 服务端获取的access_token到期时间 再减去300秒
                long endTime = Math.abs((expTime.atZone(ZoneId.systemDefault()).toEpochSecond()) - 300L);
                // 当前时间秒数
                long startTime =
                        LocalDateTime.now().atZone(ZoneId.systemDefault()).toEpochSecond();
                cacheSecond = endTime - startTime;
            }

            if (StringUtils.isNotBlank(accessToken)) {
                UapTokenUtils.saveAccessToken(session.getId(), accessToken, cacheSecond);
            } else {
                log.warn("TicketDomain 中未包含 accessToken");
            }

            if (StringUtils.isNotBlank(refreshToken)) {
                UapTokenUtils.saveRefreshToken(session.getId(), refreshToken, cacheSecond * 2);
            } else {
                log.warn("TicketDomain 中未包含 refreshToken");
            }

            log.info("无密码登录成功，用户: {}，已完成 Session 和 Token 的保存", uapUser.getLoginName());

            // 提取用户菜单路径并存入Session
            storeUserMenuPathsInSession(request);

            return AppResponse.success(uapUser);

        } catch (Exception e) {
            log.error("无密码登录失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "登录失败: " + e.getMessage());
        }
    }

    /**
     * UAP密码登录（带租户ID）并建立session
     * 用于UAP认证模式的正式登录
     *
     * @param loginName 登录账号
     * @param password 密码
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 用户信息
     */
    public UapUser loginUapByPasswordWithTenant(
            String loginName, String password, String tenantId, HttpServletRequest request) {
        try {
            log.info("开始UAP密码登录，账号: {}, 租户ID: {}", loginName, tenantId);

            // 1. 构建UAP登录请求参数
            com.iflytek.sec.uap.client.core.dto.authentication.UapLoginByPasswordDto uapLoginByPasswordDto =
                    new com.iflytek.sec.uap.client.core.dto.authentication.UapLoginByPasswordDto();
            uapLoginByPasswordDto.setAppCode(ClientConfigUtil.instance().getAppCode());
            uapLoginByPasswordDto.setService(ClientConfigUtil.instance().getCasClientContext());
            uapLoginByPasswordDto.setRedirect(ClientConfigUtil.instance().getCasClientContext());
            uapLoginByPasswordDto.setLoginName(loginName);
            uapLoginByPasswordDto.setPassword(password);
            uapLoginByPasswordDto.setTenantId(tenantId);
            uapLoginByPasswordDto.setReferer(ClientConfigUtil.instance().getRestServerUrl());

            // 2. 调用UAP登录接口获取ticket
            ResponseDto<com.iflytek.sec.uap.client.core.dto.authentication.LoginResultDto> loginResponse =
                    ClientAuthenticationAPI.loginUapByPassword(uapLoginByPasswordDto);

            if (loginResponse == null || !loginResponse.isFlag()) {
                String errorMsg = loginResponse != null ? loginResponse.getMessage() : "UAP登录响应为空";
                log.error("UAP登录失败：{}", errorMsg);
                throw new ServiceException("UAP登录失败：" + errorMsg);
            }

            com.iflytek.sec.uap.client.core.dto.authentication.LoginResultDto loginResult = loginResponse.getData();
            if (loginResult == null || StringUtils.isBlank(loginResult.getTicket())) {
                log.error("UAP登录响应中未包含有效的ticket");
                throw new ServiceException("UAP登录失败：未返回有效的ticket");
            }

            String ticket = loginResult.getTicket();
            String service = ClientConfigUtil.instance().getCasClientContext();

            // 3. 调用 ClientAuthenticationAPI.validateTicket 验证 ticket
            ResponseDto<TicketDomain> validateResponse = ClientAuthenticationAPI.validateTicket(ticket, service);

            if (validateResponse == null || !validateResponse.isFlag()) {
                String errorMsg = validateResponse != null ? validateResponse.getMessage() : "验证登录凭证失败";
                log.error("验证 ticket 失败: {}", errorMsg);
                throw new ServiceException("验证 ticket 失败: " + errorMsg);
            }

            // 4. 从 validateTicket 的返回结果中获取 UapUser
            TicketDomain ticketDomain = validateResponse.getData();
            if (ticketDomain == null) {
                throw new ServiceException("验证结果为空");
            }

            UapUser uapUser = ticketDomain.getUapUser();
            if (uapUser == null) {
                throw new ServiceException("无法从验证结果中获取用户信息");
            }

            // 5. 将用户信息保存到 session
            javax.servlet.http.HttpSession session = request.getSession(true);
            SessionUtil.getInstance().saveUser(session, uapUser);
            SessionUtil.getInstance().saveTenantId(session, tenantId);

            // 6. 从 TicketDomain 中提取并保存 accessToken 和 refreshToken 到 Redis
            String accessToken = ticketDomain.getAccessToken();
            String refreshToken = ticketDomain.getRefreshToken();

            // 通过accessToken获取租户信息
            UapTenant uapTenant = ClientAuthenticationAPI.getTenantInfo(tenantId, accessToken);
            SessionUtil.getInstance().saveTenant(session, uapTenant);

            // 7. 获取用户角色列表并保存到 session
            if (StringUtils.isNotBlank(accessToken)) {
                try {
                    List<UapRole> roleList =
                            ClientAuthenticationAPI.getUserRoleListInApp(tenantId, uapUser.getId(), accessToken);
                    if (CollectionUtil.isEmpty(roleList)) {
                        log.warn("用户 {} 在租户 {} 中没有角色，尝试分配注册角色", uapUser.getLoginName(), tenantId);
                        roleList = assignRegisterRoleIfNeeded(
                                tenantId, uapUser.getId(), accessToken, uapUser.getLoginName());
                    }

                    // 保存角色列表到 session
                    if (!CollectionUtil.isEmpty(roleList)) {
                        SessionUtil.getInstance().saveUserRole(session, roleList);
                    }
                } catch (Exception e) {
                    log.warn("获取用户角色列表失败，但不影响登录：{}", e.getMessage());
                }
            }

            // 8. 保存 token 到 Redis
            LocalDateTime expTime = ticketDomain.getExpTime();
            Long cacheSecond = 0L;
            if (null == expTime) {
                cacheSecond = 7200L;
            } else {
                // 服务端获取的access_token到期时间 再减去300秒
                long endTime = Math.abs((expTime.atZone(ZoneId.systemDefault()).toEpochSecond()) - 300L);
                // 当前时间秒数
                long startTime =
                        LocalDateTime.now().atZone(ZoneId.systemDefault()).toEpochSecond();
                cacheSecond = endTime - startTime;
            }

            if (StringUtils.isNotBlank(accessToken)) {
                UapTokenUtils.saveAccessToken(session.getId(), accessToken, cacheSecond);
            } else {
                log.warn("TicketDomain 中未包含 accessToken");
            }

            if (StringUtils.isNotBlank(refreshToken)) {
                UapTokenUtils.saveRefreshToken(session.getId(), refreshToken, cacheSecond * 2);
            } else {
                log.warn("TicketDomain 中未包含 refreshToken");
            }

            log.info("UAP密码登录成功，用户: {}，已完成 Session 和 Token 的保存", uapUser.getLoginName());

            // 提取用户菜单路径并存入Session
            storeUserMenuPathsInSession(request);

            return uapUser;

        } catch (ServiceException e) {
            throw e;
        } catch (Exception e) {
            log.error("UAP密码登录失败", e);
            throw new ServiceException("UAP密码登录失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<User> getCurrentLoginUser(HttpServletRequest request) {
        try {
            UapUser uapUser = UserUtils.nowLoginUser();
            User user = userMapper.fromUapUser(uapUser);
            return AppResponse.success(user);
        } catch (com.iflytek.rpa.auth.exception.NoLoginException e) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户未登录");
        } catch (Exception e) {
            log.error("获取当前登录用户失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getCurrentUserId(HttpServletRequest request) {
        try {
            String userId = UserUtils.nowUserId();
            return AppResponse.success(userId);
        } catch (com.iflytek.rpa.auth.exception.NoLoginException e) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户未登录");
        } catch (Exception e) {
            log.error("获取当前登录用户ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getCurrentLoginUsername(HttpServletRequest request) {
        try {
            String loginName = UserUtils.nowLoginUsername();
            return AppResponse.success(loginName);
        } catch (com.iflytek.rpa.auth.exception.NoLoginException e) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户未登录");
        } catch (Exception e) {
            log.error("获取当前登录用户名失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getLoginNameById(String id, HttpServletRequest request) {
        try {
            String loginName = UserUtils.getLoginNameById(id);
            if (loginName == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            return AppResponse.success(loginName);
        } catch (Exception e) {
            log.error("根据用户ID查询登录名失败, userId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询登录名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getRealNameById(String id, HttpServletRequest request) {
        try {
            String realName = UserUtils.getRealNameById(id);
            if (realName == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            return AppResponse.success(realName);
        } catch (Exception e) {
            log.error("根据用户ID查询姓名失败, userId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询姓名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<User> getUserInfoById(String id, HttpServletRequest request) {
        try {

            UapUser uapUser = userDao.getUserById(id, databaseName);
            if (uapUser == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            User user = userMapper.fromUapUser(uapUser);
            return AppResponse.success(user);
        } catch (Exception e) {
            log.error("根据用户ID查询用户信息失败, userId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getRealNameByPhone(String phone, HttpServletRequest request) {
        try {
            String realName = UserUtils.getRealNameByPhone(phone);
            if (realName == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            return AppResponse.success(realName);
        } catch (Exception e) {
            log.error("根据手机号查询用户姓名失败, phone: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户姓名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getLoginNameByPhone(String phone, HttpServletRequest request) {
        try {
            String loginName = UserUtils.getLoginNameByPhone(phone);
            if (loginName == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            return AppResponse.success(loginName);
        } catch (Exception e) {
            log.error("根据手机号查询登录名失败, phone: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询登录名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Boolean> isHistoryUser(String phone) {
        try {
            if (StringUtils.isEmpty(phone)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "手机号不能为空");
            }
            String extInfo = userDao.queryExtInfoByPhone(phone, databaseName);
            boolean history = "1".equals(extInfo);
            return AppResponse.success(history);
        } catch (Exception e) {
            log.error("查询历史用户失败, phone: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询历史用户失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<User> getUserInfoByPhone(String phone, HttpServletRequest request) {
        try {
            UapUser uapUser = UserUtils.getUserInfoByPhone(phone);
            if (uapUser == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            User user = userMapper.fromUapUser(uapUser);
            return AppResponse.success(user);
        } catch (Exception e) {
            log.error("根据手机号查询用户信息失败, phone: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<User>> queryUserListByIds(List<String> userIdList, HttpServletRequest request) {
        try {
            if (CollectionUtil.isEmpty(userIdList)) {
                return AppResponse.success(Collections.emptyList());
            }
            List<UapUser> uapUsers = UserUtils.queryUserPageList(userIdList);
            List<User> users = userMapper.fromUapUsers(uapUsers);
            return AppResponse.success(users);
        } catch (Exception e) {
            log.error("根据用户ID列表查询用户信息失败, userIds: {}", userIdList, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<User>> searchUserByName(String keyword, String deptId, HttpServletRequest request) {
        try {
            List<UapUser> uapUsers = UserUtils.searchUserByName(keyword, deptId);
            if (uapUsers == null) {
                return AppResponse.success(Collections.emptyList());
            }
            List<User> users = userMapper.fromUapUsers(uapUsers);
            return AppResponse.success(users);
        } catch (Exception e) {
            log.error("根据姓名模糊查询人员失败, keyword: {}, deptId: {}", keyword, deptId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<User>> searchUserByPhone(String keyword, String deptId, HttpServletRequest request) {
        try {
            List<UapUser> uapUsers = UserUtils.searchUserByPhone(keyword, deptId);
            if (uapUsers == null) {
                return AppResponse.success(Collections.emptyList());
            }
            List<User> users = userMapper.fromUapUsers(uapUsers);
            return AppResponse.success(users);
        } catch (Exception e) {
            log.error("根据手机号模糊查询人员失败, keyword: {}, deptId: {}", keyword, deptId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<User>> searchUserByNameOrPhone(String keyword, String deptId, HttpServletRequest request) {
        try {
            List<UapUser> uapUsers = UserUtils.searchUserByNameOrPhone(keyword, deptId);
            if (CollectionUtil.isEmpty(uapUsers)) {
                return AppResponse.success(Collections.emptyList());
            }
            List<User> users = userMapper.fromUapUsers(uapUsers);
            return AppResponse.success(users);
        } catch (Exception e) {
            log.error("根据姓名或手机号模糊查询人员失败, keyword: {}, deptId: {}", keyword, deptId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户信息失败: " + e.getMessage());
        }
    }

    /**
     * 查询当前登录的用户信息
     * @param request HTTP请求
     * @return 用户信息
     */
    @Override
    public AppResponse<User> getUserInfo(HttpServletRequest request) {

        UapUser uapLoginUser = UapUserInfoAPI.getLoginUser(request);
        User user = userMapper.fromUapUser(uapLoginUser);
        return AppResponse.success(user);
    }

    /**
     * 查询当前机构的全部用户(部门新增，部门负责人下拉框)
     * @param orgId 部门ID
     * @param request HTTP请求
     * @return 用户列表
     */
    @Override
    public AppResponse<List<User>> queryUserDetailListByOrgId(String orgId, HttpServletRequest request) {
        if (StringUtils.isBlank(orgId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少部门id");
        }
        List<UserExtendDto> userExtendList =
                ClientManagementAPI.queryUserDetailListByOrgId(UapUserInfoAPI.getTenantId(request), orgId);
        List<UapUser> uapUserList = new ArrayList<>();
        for (UserExtendDto user : userExtendList) {
            if (user == null || user.getUser() == null) {
                continue;
            }
            uapUserList.add(user.getUser());
        }
        List<User> userList = userMapper.fromUapUsers(uapUserList);
        return AppResponse.success(userList);
    }

    /**
     * 注册后更新密码（使用默认初始密码作为旧密码）
     *
     * @param loginName 登录名
     * @param newPassword 新密码
     */
    public void updatePasswordAfterRegister(String loginName, String newPassword) {
        try {
            UpdatePwdDto updatePwdDto = new UpdatePwdDto();
            updatePwdDto.setLoginName(loginName);
            updatePwdDto.setOldPwd(
                    Base64Utils.encodeToString(UAPConstant.DEFAULT_INITIAL_PASSWORD.getBytes(StandardCharsets.UTF_8)));
            updatePwdDto.setNewPwd(Base64Utils.encodeToString(newPassword.getBytes(StandardCharsets.UTF_8)));

            ResponseDto<String> updatePwdResponse = ClientAuthenticationAPI.updateUserPwd(updatePwdDto);

            if (!updatePwdResponse.isFlag()) {
                throw new ServiceException("更新密码失败：" + updatePwdResponse.getMessage());
            }

            log.info("注册后更新密码成功，登录名：{}", loginName);

        } catch (Exception e) {
            log.error("注册后更新密码失败，登录名：{}", loginName, e);
            throw new ServiceException("更新密码失败：" + e.getMessage());
        }
    }

    /**
     * 退出登录
     * @param request HTTP请求
     * @param response HTTP响应
     * @return 操作结果
     */
    @Override
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) {
        try {
            // 清除单点登录的session映射
            try {
                UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
                if (loginUser != null && StringUtils.isNotBlank(loginUser.getId())) {
                    String redisKey = REDIS_KEY_USER_SESSION_PREFIX + loginUser.getId();
                    RedisUtils.del(redisKey);
                    log.debug("已清除单点登录session映射，用户ID：{}", loginUser.getId());
                }
            } catch (Exception e) {
                log.warn("清除单点登录session映射失败", e);
                // 不抛出异常，继续执行退出登录
            }

            UapUserInfoAPI.logout(request, response);
            // 手动设置cookie
            Cookie cookie = new Cookie("SESSION", "");
            cookie.setMaxAge(0); // 设置最大存活时间为 0
            cookie.setPath("/"); // 设置路径，确保与原路径一致
            response.addCookie(cookie); // 添加到响应中

            return AppResponse.success("退出登录成功");
        } catch (Exception e) {
            log.error("退出登录失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "退出登录失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> changeDept(UserChangeDeptDto userChangeDeptDto, HttpServletRequest request) {
        /*
        变更部门或角色只能通过updateUser接口，资源池相关接口没有没有更新部门或角色的功能
         */
        List<com.iflytek.rpa.auth.core.entity.UpdateUserDto> userList = userChangeDeptDto.getUserList();
        String deptId = userChangeDeptDto.getDeptId();
        if (CollectionUtil.isEmpty(userList) || StringUtils.isBlank(deptId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        for (com.iflytek.rpa.auth.core.entity.UpdateUserDto userInfo : userList) {
            if (null == userInfo || StringUtils.isBlank(userInfo.getId())) {
                continue;
            }
            // 根据id查询用户信息
            UapUser user = UserUtils.getUserInfoById(userInfo.getId());
            // 设置用户信息
            userInfo.setName(user.getName());
            // 类型为资源池用户
            userInfo.setUserType(3);
            userInfo.setLoginName(user.getLoginName());
            userInfo.setPhone(user.getPhone());
            userInfo.setEmail(user.getEmail());

            // 更新状态信息
            com.iflytek.rpa.auth.core.entity.UpdateUapUserDto updateUapUserDto =
                    new com.iflytek.rpa.auth.core.entity.UpdateUapUserDto();
            userInfo.setOrgId(deptId);
            updateUapUserDto.setUser(userInfo);
            // 转换为UAP的UpdateUapUserDto
            UpdateUapUserDto uapUpdateUapUserDto = updateUapUserDtoMapper.toUapUpdateUapUserDto(updateUapUserDto);
            ResponseDto<String> updateUserResponse = managementClient.updateUser(uapUpdateUapUserDto);
            if (!updateUserResponse.isFlag()) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, updateUserResponse.getMessage());
            }
        }
        return AppResponse.success("操作成功");
    }

    /**
     * 卓越中心-机器人看板-所有者下拉选择-查询接口
     * 根据输入的关键字（姓名或手机号）查询用户
     * @param keyword 关键字（姓名或手机号）
     * @param deptId 部门ID
     * @return 用户搜索结果列表
     */
    @Override
    public AppResponse<List<UserSearchDto>> getUserByNameOrPhone(
            String keyword, String deptId, HttpServletRequest request) {
        List<UapUser> userList = UserUtils.searchUserByNameOrPhone(keyword, deptId);
        if (CollectionUtil.isEmpty(userList)) {
            return AppResponse.success(new ArrayList<>());
        }
        List<UserSearchDto> result = new ArrayList<>();
        // 使用 Set 过滤重复用户（以用户ID为唯一标识）
        Set<String> userIdSet = new HashSet<>();
        for (UapUser user : userList) {
            if (user == null || userIdSet.contains(user.getId())) {
                continue;
            }
            userIdSet.add(user.getId());
            UserSearchDto userSearchDto = new UserSearchDto();
            BeanUtils.copyProperties(user, userSearchDto);
            result.add(userSearchDto);
        }
        return AppResponse.success(result);
    }

    /**
     * 获取用户详细信息（包含扩展信息等）
     * @param tenantId 租户ID
     * @param getUserDto 查询参数
     * @param request HTTP请求
     * @return 用户扩展信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.UserExtendDto> queryUserExtendInfo(
            String tenantId, com.iflytek.rpa.auth.core.entity.GetUserDto getUserDto, HttpServletRequest request) {
        // getUserDto 转换为 UAP 的 GetUserDto
        GetUserDto uapGetUserDto = getUserDtoMapper.toUapGetUserDto(getUserDto);
        // 调用 UAP 接口获取用户扩展信息
        UserExtendDto uapUserExtendInfo = ClientManagementAPI.getUserExtendInfo(tenantId, uapGetUserDto);
        // 转换为 core 的 UserExtendDto
        com.iflytek.rpa.auth.core.entity.UserExtendDto coreUserExtendDto =
                userExtendDtoMapper.fromUapUserExtendDto(uapUserExtendInfo);
        return AppResponse.success(coreUserExtendDto);
    }

    /**
     * 获取当前登录用户的权益
     * 根据session查询租户code，判断如果是企业租户，则查询数据库中权益
     * 如果没有数据，默认拥有所有权益
     *
     * @param request HTTP请求
     * @return 用户权益信息
     */
    @Override
    public AppResponse<UserEntitlementDto> getCurrentUserEntitlement(HttpServletRequest request) {
        try {
            // 1. 获取当前登录用户
            UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
            if (loginUser == null || StringUtils.isBlank(loginUser.getId())) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户失败");
            }
            String userId = loginUser.getId();

            // 2. 获取租户信息
            UapTenant uapTenant = UapUserInfoAPI.getTenant(request);
            if (uapTenant == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户信息失败");
            }

            String tenantCode = uapTenant.getTenantCode();
            String tenantId = uapTenant.getId();

            if (StringUtils.isBlank(tenantCode)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "租户编码为空");
            }

            // 3. 判断是否为企业租户
            boolean isEnterpriseTenant = isEnterpriseTenant(tenantCode);

            // 4. 如果不是企业租户，返回默认所有权益
            if (!isEnterpriseTenant) {
                UserEntitlementDto defaultDto = createDefaultEntitlement();
                log.info("非企业租户，返回默认权益，userId: {}, tenantId: {}", userId, tenantId);
                return AppResponse.success(defaultDto);
            }

            // 5. 如果是企业租户，查询数据库中的权益
            UserEntitlement entitlement = userEntitlementDao.queryByUserIdAndTenantId(userId, tenantId);

            // 6. 如果没有数据，返回默认所有权益
            if (entitlement == null) {
                UserEntitlementDto defaultDto = createDefaultEntitlement();
                log.info("企业租户但未配置权益，返回默认权益，userId: {}, tenantId: {}", userId, tenantId);
                return AppResponse.success(defaultDto);
            }

            // 7. 如果有数据，转换为DTO返回
            UserEntitlementDto dto = convertToDto(entitlement);
            log.info(
                    "查询用户权益成功，userId: {}, tenantId: {}, designer: {}, executor: {}, console: {}, market: {}",
                    userId,
                    tenantId,
                    dto.getModuleDesigner(),
                    dto.getModuleExecutor(),
                    dto.getModuleConsole(),
                    dto.getModuleMarket());
            return AppResponse.success(dto);

        } catch (Exception e) {
            log.error("获取当前用户权益失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前用户权益失败: " + e.getMessage());
        }
    }

    /**
     * 判断是否为企业租户
     *
     * @param tenantCode 租户编码
     * @return true-企业租户，false-非企业租户
     */
    private boolean isEnterpriseTenant(String tenantCode) {
        if (StringUtils.isBlank(tenantCode)) {
            return false;
        }
        return tenantCode.startsWith(UAPConstant.ENTERPRISE_PURCHASED_TENANT_CODE)
                || tenantCode.startsWith(UAPConstant.ENTERPRISE_SUBSCRIPTION_TENANT_CODE);
    }

    /**
     * 创建默认权益（所有模块都有权限）
     *
     * @return 默认权益DTO
     */
    private UserEntitlementDto createDefaultEntitlement() {
        UserEntitlementDto dto = new UserEntitlementDto();
        dto.setModuleDesigner(true);
        dto.setModuleExecutor(true);
        dto.setModuleConsole(true);
        dto.setModuleMarket(true);
        return dto;
    }

    /**
     * 将实体类转换为DTO
     *
     * @param entitlement 用户权益实体
     * @return 用户权益DTO
     */
    private UserEntitlementDto convertToDto(UserEntitlement entitlement) {
        UserEntitlementDto dto = new UserEntitlementDto();
        dto.setModuleDesigner(entitlement.getModuleDesigner() != null && entitlement.getModuleDesigner() == 1);
        dto.setModuleExecutor(entitlement.getModuleExecutor() != null && entitlement.getModuleExecutor() == 1);
        dto.setModuleConsole(entitlement.getModuleConsole() != null && entitlement.getModuleConsole() == 1);
        dto.setModuleMarket(entitlement.getModuleMarket() != null && entitlement.getModuleMarket() == 1);
        return dto;
    }

    @Override
    public AppResponse<String> getNameById(String id, HttpServletRequest request) {
        try {
            String name = userDao.getNameById(id, databaseName);
            if (StringUtils.isEmpty(name)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到用户信息");
            }
            return AppResponse.success(name);
        } catch (Exception e) {
            log.error("根据用户ID查询用户姓名失败, userId: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询用户姓名失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<RobotExecute>> getDeployedUserList(
            GetDeployedUserListDto dto, HttpServletRequest request) {
        try {
            if (dto.getPageNo() == null || dto.getPageNo() < 1) {
                dto.setPageNo(1);
            }
            if (dto.getPageSize() == null || dto.getPageSize() < 1) {
                dto.setPageSize(10);
            }

            Page<RobotExecute> page = new Page<>(dto.getPageNo(), dto.getPageSize());

            IPage<RobotExecute> result = userDao.getDeployedUserList(page, dto, databaseName);

            com.iflytek.rpa.auth.core.entity.PageDto<RobotExecute> pageDto =
                    new com.iflytek.rpa.auth.core.entity.PageDto<>();
            pageDto.setResult(result.getRecords());
            pageDto.setTotalCount(result.getTotal());
            pageDto.setCurrentPageNo((int) result.getCurrent());
            pageDto.setPageSize((int) result.getSize());

            return AppResponse.success(pageDto);
        } catch (Exception e) {
            log.error("获取已部署用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取已部署用户列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<RobotExecute>> getDeployedUserListWithoutTenantId(
            GetDeployedUserListDto dto, HttpServletRequest request) {
        try {
            if (dto.getPageNo() == null || dto.getPageNo() < 1) {
                dto.setPageNo(1);
            }
            if (dto.getPageSize() == null || dto.getPageSize() < 1) {
                dto.setPageSize(10);
            }
            Page<RobotExecute> page = new Page<>(dto.getPageNo(), dto.getPageSize());

            IPage<RobotExecute> result = userDao.getDeployedUserListWithoutTenantId(page, dto, databaseName);

            com.iflytek.rpa.auth.core.entity.PageDto<RobotExecute> pageDto =
                    new com.iflytek.rpa.auth.core.entity.PageDto<>();
            pageDto.setResult(result.getRecords());
            pageDto.setTotalCount(result.getTotal());
            pageDto.setCurrentPageNo((int) result.getCurrent());
            pageDto.setPageSize((int) result.getSize());
            return AppResponse.success(pageDto);
        } catch (Exception e) {
            log.error("获取已部署用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取已部署用户列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<MarketDto>> getUserUnDeployed(GetUserUnDeployedDto dto, HttpServletRequest request) {
        try {
            List<MarketDto> result = userDao.getUserUnDeployed(dto, databaseName);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("获取未部署用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取未部署用户列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<MarketDto>> getMarketUserList(
            GetMarketUserListDto dto, HttpServletRequest request) {
        try {
            if (dto.getPageNo() == null || dto.getPageNo() < 1) {
                dto.setPageNo(1);
            }
            if (dto.getPageSize() == null || dto.getPageSize() < 1) {
                dto.setPageSize(10);
            }

            Page<MarketDto> page = new Page<>(dto.getPageNo(), dto.getPageSize(), true);

            IPage<MarketDto> result = userDao.getMarketUserList(page, dto, databaseName);

            com.iflytek.rpa.auth.core.entity.PageDto<MarketDto> pageDto =
                    new com.iflytek.rpa.auth.core.entity.PageDto<>();
            pageDto.setResult(result.getRecords());
            pageDto.setTotalCount(result.getTotal());
            pageDto.setCurrentPageNo((int) result.getCurrent());
            pageDto.setPageSize((int) result.getSize());

            return AppResponse.success(pageDto);
        } catch (Exception e) {
            log.error("获取市场用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取市场用户列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.PageDto<MarketDto>> getMarketUserListByPublic(
            GetMarketUserListByPublicDto dto, HttpServletRequest request) {
        try {
            if (dto.getPageNo() == null || dto.getPageNo() < 1) {
                dto.setPageNo(1);
            }
            if (dto.getPageSize() == null || dto.getPageSize() < 1) {
                dto.setPageSize(10);
            }

            Page<MarketDto> page = new Page<>(dto.getPageNo(), dto.getPageSize(), true);

            IPage<MarketDto> result = userDao.getMarketUserListByPublic(page, dto, databaseName);

            com.iflytek.rpa.auth.core.entity.PageDto<MarketDto> pageDto =
                    new com.iflytek.rpa.auth.core.entity.PageDto<>();
            pageDto.setResult(result.getRecords());
            pageDto.setTotalCount(result.getTotal());
            pageDto.setCurrentPageNo((int) result.getCurrent());
            pageDto.setPageSize((int) result.getSize());

            return AppResponse.success(pageDto);
        } catch (Exception e) {
            log.error("获取公共市场用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取公共市场用户列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<MarketDto>> getMarketUserByPhone(GetMarketUserByPhoneDto dto, HttpServletRequest request) {
        try {
            List<MarketDto> result = userDao.getMarketUserByPhone(dto, databaseName);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("根据手机号查询市场用户失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据手机号查询市场用户失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<MarketDto>> getMarketUserByPhoneForOwner(
            GetMarketUserByPhoneForOwnerDto dto, HttpServletRequest request) {
        try {
            List<MarketDto> result = userDao.getMarketUserByPhoneForOwner(dto, databaseName);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("根据手机号查询市场中的用户失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据手机号查询市场中的用户失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<TenantUser>> getMarketTenantUserList(
            GetMarketTenantUserListDto dto, HttpServletRequest request) {
        try {
            List<TenantUser> result = userDao.getMarketTenantUserList(dto, databaseName);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("根据用户ID列表查询租户用户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据用户ID列表查询租户用户列表失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前用户权限列表（casdoor的功能接口）
     * @param request HTTP请求
     * @return 用户列表
     */
    @Override
    public AppResponse<List<Permission>> getCurrentUserPermissionList(HttpServletRequest request) throws IOException {
        throw new UnsupportedOperationException("不支持的功能");
    }

    /**
     * （casdoor的功能接口）
     * @param request HTTP请求
     * @return
     */
    @Override
    public AppResponse<String> getRedirectUrl(HttpServletRequest request) {
        throw new UnsupportedOperationException("不支持的功能");
    }

    /**
     * （casdoor的功能接口）
     * @param code OAuth授权码
     * @param state OAuth state参数
     * @param request HTTP请求
     * @return
     * @throws IOException
     */
    @Override
    public AppResponse<User> signIn(String code, String state, HttpServletRequest request) throws IOException {
        throw new UnsupportedOperationException("不支持的功能");
    }

    /**
     * （casdoor的功能接口）
     * @param request HTTP请求
     * @return
     */
    @Override
    public AppResponse<User> checkLoginStatus(HttpServletRequest request) {
        throw new UnsupportedOperationException("不支持的功能");
    }

    /**
     * （casdoor的功能接口）
     * @param request HTTP请求
     * @return
     */
    @Override
    public AppResponse<String> refreshToken(HttpServletRequest request) {
        throw new UnsupportedOperationException("不支持的功能");
    }

    /**
     * 提取用户菜单路径并存入Session
     * @param request HTTP请求
     */
    private void storeUserMenuPathsInSession(HttpServletRequest request) {
        try {
            // 获取用户菜单树
            AppResponse<List<TreeNode>> menuTreeResponse = authService.getUserAuthTreeInApp(request);
            if (!menuTreeResponse.ok() || menuTreeResponse.getData() == null) {
                log.warn("获取用户菜单树失败，无法存储菜单路径到Session");
                return;
            }

            // 提取菜单路径列表
            List<TreeNode> menuTreeList = menuTreeResponse.getData();
            Set<String> menuPaths = extractMenuPaths(menuTreeList);

            // 存入Session
            javax.servlet.http.HttpSession session = request.getSession(false);
            if (session != null) {
                session.setAttribute("userMenuPaths", menuPaths);
                log.debug("用户菜单路径已存入Session，共{}条路径", menuPaths.size());
            } else {
                log.warn("Session不存在，无法存储菜单路径");
            }
        } catch (Exception e) {
            log.error("提取并存储用户菜单路径到Session失败", e);
            // 不抛出异常，避免影响登录流程
        }
    }

    /**
     * 从菜单树中提取所有菜单路径
     * @param treeNodeList 菜单树列表
     * @return 菜单路径集合（去重）
     */
    private Set<String> extractMenuPaths(List<TreeNode> treeNodeList) {
        Set<String> menuPaths = new HashSet<>();
        if (treeNodeList == null || treeNodeList.isEmpty()) {
            return menuPaths;
        }

        for (TreeNode rootNode : treeNodeList) {
            // 从根节点开始递归，初始路径前缀为空字符串
            extractPathsFromNode(rootNode, "", menuPaths);
        }

        return menuPaths;
    }

    /**
     * 递归提取节点及其子节点的路径
     * @param node 当前节点
     * @param parentPath 父节点路径前缀（如 "/schedule"）
     * @param menuPaths 路径集合
     */
    private void extractPathsFromNode(TreeNode node, String parentPath, Set<String> menuPaths) {
        if (node == null) {
            return;
        }

        String nodeValue = node.getValue();
        String currentPath = parentPath;

        // 如果当前节点有value，则拼接到路径中
        if (StringUtils.isNotBlank(nodeValue)) {
            // 构建完整路径：父路径 + "/" + 当前节点value
            if (StringUtils.isBlank(parentPath)) {
                // 如果父路径为空，直接使用当前节点value，并添加前导斜杠
                currentPath = "/" + nodeValue.trim();
            } else {
                // 如果父路径不为空，拼接父路径和当前节点value
                currentPath = parentPath + "/" + nodeValue.trim();
            }
            // 标准化路径
            currentPath = normalizeMenuPath(currentPath);
        }

        // 递归处理子节点，将当前路径作为子节点的父路径
        List<TreeNode> children = node.getNodes();
        if (children != null && !children.isEmpty()) {
            // 有子节点，继续递归，不添加到路径集合
            for (TreeNode child : children) {
                // 如果当前节点有value，使用currentPath作为子节点的父路径
                // 如果当前节点没有value，继续使用parentPath
                String childParentPath = StringUtils.isNotBlank(nodeValue) ? currentPath : parentPath;
                extractPathsFromNode(child, childParentPath, menuPaths);
            }
        } else {
            // 没有子节点，说明是叶子节点，将完整路径添加到集合中
            if (StringUtils.isNotBlank(currentPath)) {
                menuPaths.add(currentPath);
            }
        }
    }

    /**
     * 标准化菜单路径
     * 去除尾部斜杠，确保路径格式统一（如 /schedule/task）
     * @param path 原始路径
     * @return 标准化后的路径
     */
    private String normalizeMenuPath(String path) {
        if (StringUtils.isBlank(path)) {
            return path;
        }
        path = path.trim();
        // 去除尾部斜杠（但保留根路径 "/"）
        if (path.endsWith("/") && path.length() > 1) {
            path = path.substring(0, path.length() - 1);
        }
        return path;
    }
}
