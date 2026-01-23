package com.iflytek.rpa.auth.sp.uap.service.impl;

import static com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant.REDIS_KEY_TENANT_EXPIRATION_PREFIX;
import static com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant.REDIS_KEY_TENANT_HAS_SPACE_PREFIX;
import static com.iflytek.rpa.auth.sp.uap.constants.RedisKeyConstant.REDIS_KEY_TENANT_USER_PREFIX;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.conf.condition.ConditionalOnSaaSOrUAP;
import com.iflytek.rpa.auth.core.entity.Org;
import com.iflytek.rpa.auth.core.entity.Tenant;
import com.iflytek.rpa.auth.core.entity.TenantExpirationDto;
import com.iflytek.rpa.auth.core.entity.TenantInfoDto;
import com.iflytek.rpa.auth.core.entity.UserVo;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.exception.ServiceException;
import com.iflytek.rpa.auth.sp.uap.constants.UAPConstant;
import com.iflytek.rpa.auth.sp.uap.dao.TenantDao;
import com.iflytek.rpa.auth.sp.uap.dao.TenantExpirationDao;
import com.iflytek.rpa.auth.sp.uap.dao.UserDao;
import com.iflytek.rpa.auth.sp.uap.entity.TenantExpiration;
import com.iflytek.rpa.auth.sp.uap.mapper.OrgMapper;
import com.iflytek.rpa.auth.sp.uap.mapper.TenantMapper;
import com.iflytek.rpa.auth.sp.uap.utils.EncryptUtils;
import com.iflytek.rpa.auth.sp.uap.utils.TenantUtils;
import com.iflytek.rpa.auth.sp.uap.utils.UapManagementClientUtil;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import com.iflytek.rpa.auth.utils.RedisUtils;
import com.iflytek.sec.uap.client.api.ClientAuthenticationAPI;
import com.iflytek.sec.uap.client.api.ClientManagementAPI;
import com.iflytek.sec.uap.client.api.UapUserInfoAPI;
import com.iflytek.sec.uap.client.core.client.ManagementClient;
import com.iflytek.sec.uap.client.core.dto.ResponseDto;
import com.iflytek.sec.uap.client.core.dto.app.UapApp;
import com.iflytek.sec.uap.client.core.dto.org.UapOrg;
import com.iflytek.sec.uap.client.core.dto.tenant.*;
import com.iflytek.sec.uap.client.core.dto.user.GetUserDto;
import com.iflytek.sec.uap.client.core.dto.user.UapUser;
import com.iflytek.sec.uap.client.core.dto.user.UserExtendDto;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

@Slf4j
@Service("tenantService")
@ConditionalOnSaaSOrUAP
public class TenantServiceImpl implements TenantService {
    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    private TenantDao tenantDao;

    @Autowired
    private UserDao userDao;

    @Autowired
    private TenantMapper tenantMapper;

    @Autowired
    private OrgMapper orgMapper;

    @Autowired
    private TenantExpirationDao tenantExpirationDao;

    @Value("${tenant.expiration.alert.days:10}")
    private Integer alertDays;

    /**
     * 租户空间信息缓存过期时间（秒）
     * 包括：用户是否在租户空间中、租户到期信息等
     * 默认2小时（7200秒）
     */
    private static final int TENANT_SPACE_CACHE_EXPIRE_SECONDS = 7200;

    /**
     * 租户空间信息空值标记缓存过期时间（秒）
     * 用于缓存"没有数据"的情况，避免频繁查询数据库
     * 默认2小时（7200秒）
     */
    private static final int TENANT_SPACE_EMPTY_CACHE_EXPIRE_SECONDS = 7200;

    private static final char TENANT_NAME_SEPARATOR = '#';

    @Override
    public AppResponse<List<UserVo>> getAllUser(String userName) throws Exception {
        String tenantId = TenantUtils.getTenantId();
        String redisKey = REDIS_KEY_TENANT_USER_PREFIX + tenantId + ":" + userName;
        Object cache = RedisUtils.get(redisKey);
        if (cache != null && StringUtils.isNotBlank(cache.toString())) {
            ObjectMapper objectMapper = new ObjectMapper();
            List<UserVo> cachedList = objectMapper.readValue(
                    cache.toString(), objectMapper.getTypeFactory().constructCollectionType(List.class, UserVo.class));
            return AppResponse.success(cachedList);
        }
        List<UserVo> allList = tenantDao.getUserByTenantId(databaseName, tenantId, userName);
        // 通过set进行过滤
        Set<UserVo> userVoSet = new HashSet<>(allList);
        List<UserVo> result = new ArrayList<>(userVoSet);
        RedisUtils.set(redisKey, new ObjectMapper().writeValueAsString(result), 3600);
        return AppResponse.success(allList);
    }

    @Override
    public AppResponse<List<Tenant>> getTenantListInApp(HttpServletRequest request) {
        List<UapTenant> uapTenantList = UapUserInfoAPI.getTenantListInApp(request);
        List<Tenant> tenantList = uapTenantList.stream()
                .map(tenantMapper::fromUapTenant)
                .filter(Objects::nonNull)
                .map(this::stripTenantNameSalt)
                .collect(Collectors.toList());
        return AppResponse.success(tenantList);
    }

    @Override
    public AppResponse<TenantInfoDto> getTenantInfo(HttpServletRequest request) throws Exception {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        // 查询租户信息
        TenantDetailDto tenantDetailDto = getTenantDetail(tenantId, request);
        TenantInfoDto tenantInfoDto = new TenantInfoDto();
        tenantInfoDto.setId(tenantDetailDto.getId());
        tenantInfoDto.setName(tenantDetailDto.getName());
        tenantInfoDto.setCode(tenantDetailDto.getTenantCode());
        // User类不是public类型的， 使用适配器
        List<?> adminList = tenantDetailDto.getAdminList();
        if (adminList != null && !adminList.isEmpty()) {
            UserAdapter userAdapter = new UserAdapter(adminList.get(0));
            String managerId = userAdapter.getId();
            String managerName = userAdapter.getName();
            tenantInfoDto.setManagerId(managerId);
            // 根据用户id查询电话
            GetUserDto getUserDto = new GetUserDto();
            getUserDto.setUserId(managerId);
            UserExtendDto userExtendDto = ClientManagementAPI.getUserExtendInfo(tenantId, getUserDto);
            UapUser user = userExtendDto.getUser();
            if (user == null || StringUtils.isBlank(user.getPhone())) {
                tenantInfoDto.setManagerName(managerName + "(" + ")");
            } else {
                tenantInfoDto.setManagerName(managerName + "(" + user.getPhone() + ")");
            }
        }
        return AppResponse.success(tenantInfoDto);
    }

    @Override
    public AppResponse<String> getTenantId(HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        return AppResponse.success(tenantId);
    }

    @Override
    public AppResponse<String> getCurrentTenantId(HttpServletRequest request) {
        try {
            String tenantId = TenantUtils.getTenantId();
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户ID失败");
            }
            return AppResponse.success(tenantId);
        } catch (Exception e) {
            log.error("获取当前登录的租户ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> getCurrentTenantName(HttpServletRequest request) {
        try {
            String tenantName = TenantUtils.getTenantName();
            if (StringUtils.isBlank(tenantName)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户名称失败");
            }
            return AppResponse.success(tenantName);
        } catch (Exception e) {
            log.error("获取当前登录的租户名称失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户名称失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Tenant> queryTenantInfoById(String tenantId, HttpServletRequest request) {
        try {
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }
            UapTenant uapTenant = TenantUtils.queryTenantInfoById(tenantId);
            if (uapTenant == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "未找到租户信息");
            }
            Tenant tenant = tenantMapper.fromUapTenant(uapTenant);
            return AppResponse.success(tenant);
        } catch (Exception e) {
            log.error("根据租户ID查询租户信息失败, tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询租户信息失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<String> changeManager(String id, HttpServletRequest request) {
        String tenantId = UapUserInfoAPI.getTenantId(request);
        UpdateTenantDto updateTenantDto = new UpdateTenantDto();
        updateTenantDto.setId(tenantId);
        List<TenantUserDto> adminList = new ArrayList<>();
        TenantUserDto tenantUserDto = new TenantUserDto();
        tenantUserDto.setId(id);
        adminList.add(tenantUserDto);
        updateTenantDto.setAdminList(adminList);
        // 查询应用信息
        UapApp appInfo = UapUserInfoAPI.getUapApp(request);
        List<TenantAppDto> appList = new ArrayList<>();
        TenantAppDto tenantAppDto = new TenantAppDto();
        tenantAppDto.setId(appInfo.getId());
        appList.add(tenantAppDto);
        updateTenantDto.setAppList(appList);
        // 查询租户信息
        TenantDetailDto tenantDetailDto = getTenantDetail(tenantId, request);
        updateTenantDto.setName(tenantDetailDto.getName());
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        // 更新管理员
        ResponseDto<String> updateResponse = managementClient.updateTenant(updateTenantDto);
        if (!updateResponse.isFlag()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, updateResponse.getMessage());
        }
        return AppResponse.success("修改成功");
    }

    @Override
    public AppResponse<List<Org>> getAllOrgList(String tenantId, HttpServletRequest request) {
        List<UapOrg> uapOrgList = ClientManagementAPI.queryAllOrgList(tenantId);
        List<Org> orgList = orgMapper.fromUapOrgs(uapOrgList);
        return AppResponse.success(orgList);
    }

    /**
     * 内部方法：根据租户ID查询租户详情
     */
    private TenantDetailDto getTenantDetail(String tenantId, HttpServletRequest request) {
        GetTenantDto getTenantDto = new GetTenantDto();
        getTenantDto.setId(tenantId);
        ManagementClient managementClient = UapManagementClientUtil.getManagementClient(request);
        ResponseDto<TenantDetailDto> tenantDetailResponse = managementClient.queryTenantDetailInfo(getTenantDto);
        if (!tenantDetailResponse.isFlag()) {
            throw new ServiceException(tenantDetailResponse.getMessage());
        }
        TenantDetailDto tenantDetailDto = tenantDetailResponse.getData();
        if (tenantDetailDto == null) {
            throw new ServiceException("数据异常，无租户信息");
        }
        return tenantDetailDto;
    }

    @Override
    public AppResponse<String> switchTenant(String tenantId, HttpServletRequest request) {
        String userId = "";
        try {
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }
            UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
            if (loginUser == null || StringUtils.isEmpty(loginUser.getId())) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户失败");
            }
            userId = loginUser.getId();

            // 验证用户是否拥有目标租户权限
            validateTenantPermission(loginUser, tenantId);

            // 执行切换租户
            UapUserInfoAPI.changeTenant(tenantId, userId, request);
            return AppResponse.success("切换租户成功");
        } catch (ServiceException e) {
            log.error("切换租户失败, tenantId: {}, userId: {}", tenantId, userId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, e.getMessage());
        } catch (Exception e) {
            log.error("切换租户失败, tenantId: {}, userId: {}", tenantId, userId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "切换租户失败: " + e.getMessage());
        }
    }

    /**
     * 验证用户是否拥有目标租户权限
     * 根据登录用户信息查询租户列表，验证目标租户ID是否在所属列表中
     *
     * @param loginUser      当前登录用户
     * @param targetTenantId 目标租户ID
     * @throws ServiceException 如果验证失败则抛出异常
     */
    private void validateTenantPermission(UapUser loginUser, String targetTenantId) {
        if (loginUser == null) {
            throw new ServiceException("用户信息不能为空");
        }
        if (StringUtils.isBlank(targetTenantId)) {
            throw new ServiceException("目标租户ID不能为空");
        }

        // 获取用户登录名
        String loginName = loginUser.getLoginName();
        if (StringUtils.isBlank(loginName)) {
            // 如果登录名为空，尝试根据手机号查询
            String phone = loginUser.getPhone();
            if (StringUtils.isNotBlank(phone)) {
                loginName = userDao.queryLoginNameByPhone(phone, databaseName);
            }
            if (StringUtils.isBlank(loginName)) {
                log.warn("无法获取用户登录名，用户ID：{}", loginUser.getId());
                loginName = phone != null ? phone : loginUser.getId();
            }
        }

        // 根据登录账号查询租户列表
        List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
        if (CollectionUtils.isEmpty(tenantList)) {
            log.warn("根据登录名未找到租户信息，登录名：{}", loginName);
            throw new ServiceException("当前用户没有可用的租户空间");
        }

        // 验证目标租户ID是否在所属列表中
        boolean hasPermission = tenantList.stream().anyMatch(tenant -> targetTenantId.equals(tenant.getId()));

        if (!hasPermission) {
            log.warn("用户没有目标租户权限，登录名：{}，目标租户ID：{}", loginName, targetTenantId);
            throw new ServiceException("您没有该租户空间的访问权限");
        }
    }

    @Override
    public AppResponse<List<Tenant>> getTenantList(String phone, HttpServletRequest request) {
        try {
            List<UapTenant> uapTenantList;
            if (StringUtils.isEmpty(phone)) {
                // 针对于登录之后，没有临时token
                //                uapTenantList = UapUserInfoAPI.getTenantListInApp(request);
                UapUser uapUser = UapUserInfoAPI.getLoginUser(request);
                phone = uapUser.getPhone();
            }
            // 根据手机号先查询用户loginName
            String loginName = userDao.queryLoginNameByPhone(phone, databaseName);
            if (StringUtils.isBlank(loginName)) {
                log.warn("根据手机号未找到用户登录名，手机号：{}", phone);
                loginName = phone;
            }

            // 根据loginName查询租户列表
            uapTenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
            //            uapTenantList = tenantDao.queryTenantListByPhone(databaseName, phone);
            // uapTenantList  将 tenantCode 以UAPConstant.PERSONAL_TENANT_CODE 开头的 排序在最后面
            uapTenantList.sort((t1, t2) -> {
                boolean isT1Personal = StringUtils.isNotBlank(t1.getTenantCode())
                        && t1.getTenantCode().startsWith(UAPConstant.PERSONAL_TENANT_CODE);
                boolean isT2Personal = StringUtils.isNotBlank(t2.getTenantCode())
                        && t2.getTenantCode().startsWith(UAPConstant.PERSONAL_TENANT_CODE);
                if (isT1Personal && !isT2Personal) {
                    return 1;
                } else if (!isT1Personal && isT2Personal) {
                    return -1;
                } else {
                    return 0;
                }
            });

            if (uapTenantList == null || uapTenantList.isEmpty()) {
                log.warn("用户没有租户信息，手机号：{}", phone);
                return AppResponse.success(Collections.emptyList());
            }

            // 3. 转换为业务实体
            List<Tenant> tenantList = uapTenantList.stream()
                    .map(tenantMapper::fromUapTenant)
                    .filter(Objects::nonNull)
                    .map(this::stripTenantNameSalt)
                    .collect(Collectors.toList());

            // 4. 为每个租户填充到期信息
            for (Tenant tenant : tenantList) {
                fillTenantExpirationInfo(tenant);
            }

            log.info("获取租户列表成功，手机号：{}，租户数量：{}", phone, tenantList.size());
            return AppResponse.success(tenantList);

        } catch (Exception e) {
            log.error("获取租户列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        }
    }

    /**
     * 去除租户名称中的随机后缀（使用最后一个 '#' 作为分隔符）。
     */
    private Tenant stripTenantNameSalt(Tenant tenant) {
        if (tenant == null) {
            return null;
        }
        String name = tenant.getName();
        if (StringUtils.isBlank(name)) {
            return tenant;
        }
        int idx = name.lastIndexOf(TENANT_NAME_SEPARATOR);
        if (idx > 0 && idx < name.length() - 1) {
            tenant.setName(name.substring(0, idx));
        }
        return tenant;
    }

    @Override
    public AppResponse<List<String>> getAllTenantId() {
        try {
            List<String> tenantIds = tenantDao.getAllTenantId(databaseName);
            return AppResponse.success(tenantIds);
        } catch (Exception e) {
            log.error("获取所有租户ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取所有租户ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<String>> getTenantManagerIds(String tenantId) {
        try {
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }
            // tenant_user_type = 1 表示租户管理员
            List<String> managerIds = tenantDao.getTenantUserIdsByType(databaseName, tenantId, 1);
            return AppResponse.success(managerIds);
        } catch (Exception e) {
            log.error("获取租户管理员ID失败, tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户管理员ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<String>> getTenantNormalUserIds(String tenantId) {
        try {
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }
            List<String> normalUserIds = tenantDao.getTenantUserIdsByType(databaseName, tenantId, 2);
            return AppResponse.success(normalUserIds);
        } catch (Exception e) {
            log.error("获取租户普通用户ID失败, tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户普通用户ID失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<String>> getNoClassifyTenantIds() {
        try {
            List<String> tenantIds = tenantDao.getNoClassifyTenantIds(databaseName);
            return AppResponse.success(tenantIds);
        } catch (Exception e) {
            log.error("获取未分类租户id失败");
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取未分类租户id失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Integer> updateTenantClassifyCompleted(List<String> ids) {
        try {
            Integer i = tenantDao.updateTenantClassifyCompleted(databaseName, ids);
            return AppResponse.success(i);
        } catch (Exception e) {
            log.error("更新租户分类完成标志失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "更新租户分类完成标志失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<String>> getAllEnterpriseTenantId() {
        try {
            List<String> tenantIds = tenantDao.getAllEnterpriseTenantId(databaseName);
            return AppResponse.success(tenantIds);
        } catch (Exception e) {
            log.error("获取所有企业租户ID列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取所有企业租户ID列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Integer> getTenantUserType(String userId, String tenantId) {
        try {
            if (StringUtils.isBlank(userId) || StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "用户ID和租户ID不能为空");
            }
            Integer tenantUserType = tenantDao.getTenantUserType(databaseName, userId, tenantId);
            return AppResponse.success(tenantUserType);
        } catch (Exception e) {
            log.error("获取租户用户类型失败, userId: {}, tenantId: {}", userId, tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户用户类型失败: " + e.getMessage());
        }
    }

    public AppResponse<TenantExpirationDto> getTenantExpiration(HttpServletRequest request) {
        try {
            // 1. 获取租户ID和编码
            String tenantId = TenantUtils.getTenantId();
            if (StringUtils.isBlank(tenantId)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户ID失败");
            }

            UapTenant uapTenant = UapUserInfoAPI.getTenant(request);
            if (uapTenant == null) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户信息失败");
            }

            String tenantCode = uapTenant.getTenantCode();
            if (StringUtils.isBlank(tenantCode)) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "租户编码为空");
            }

            // 2. 创建返回DTO并填充信息
            TenantExpirationDto dto = new TenantExpirationDto();
            dto.setTenantId(tenantId);
            dto.setTenantType(determineTenantType(tenantCode));

            // 3. 获取当前登录用户的loginName
            String loginName = null;
            try {
                UapUser loginUser = UapUserInfoAPI.getLoginUser(request);
                if (loginUser != null && StringUtils.isNotBlank(loginUser.getLoginName())) {
                    loginName = loginUser.getLoginName();
                }
            } catch (Exception e) {
                log.warn("获取当前登录用户信息失败，将跳过用户空间检查", e);
            }

            // 4. 计算并填充到期信息
            calculateAndFillExpirationInfo(dto, tenantId, tenantCode, loginName);

            log.info(
                    "查询租户到期信息成功，tenantId: {}, expirationDate: {}, remainingDays: {}, isExpired: {}, shouldAlert: {}",
                    tenantId,
                    dto.getExpirationDate(),
                    dto.getRemainingDays(),
                    dto.getIsExpired(),
                    dto.getShouldAlert());

            return AppResponse.success(dto);

        } catch (Exception e) {
            log.error("查询租户到期信息失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询租户到期信息失败: " + e.getMessage());
        }
    }

    @Override
    public boolean checkSpaceExpired(HttpServletRequest request) {
        try {
            // 复用getTenantExpiration的逻辑
            AppResponse<TenantExpirationDto> response = getTenantExpiration(request);
            if (!response.ok()) {
                // 如果查询失败，为了安全起见，不阻止访问
                log.warn("查询租户到期信息失败，不阻止访问");
                return false;
            }

            TenantExpirationDto dto = response.getData();
            if (dto == null) {
                return false;
            }

            // 返回是否到期
            return dto.getIsExpired() != null && dto.getIsExpired();
        } catch (Exception e) {
            log.error("检查空间到期状态失败", e);
            // 检查失败时，为了安全起见，不阻止访问
            return false;
        }
    }

    /**
     * 根据租户编码判断租户类型
     *
     * @param tenantCode 租户编码
     * @return 租户类型（personal/professional/enterprise_purchased/enterprise_subscription）
     */
    private String determineTenantType(String tenantCode) {
        if (tenantCode != null && tenantCode.startsWith(UAPConstant.PERSONAL_TENANT_CODE)) {
            return UAPConstant.TENANT_TYPE_PERSONAL;
        } else if (tenantCode != null && tenantCode.startsWith(UAPConstant.PROFESSIONAL_TENANT_CODE)) {
            return UAPConstant.TENANT_TYPE_PROFESSIONAL;
        } else if (tenantCode != null && tenantCode.startsWith(UAPConstant.ENTERPRISE_PURCHASED_TENANT_CODE)) {
            return UAPConstant.TENANT_TYPE_ENTERPRISE_PURCHASED;
        } else if (tenantCode != null && tenantCode.startsWith(UAPConstant.ENTERPRISE_SUBSCRIPTION_TENANT_CODE)) {
            return UAPConstant.TENANT_TYPE_ENTERPRISE_SUBSCRIPTION;
        } else {
            // 默认返回个人版
            log.warn("未知的租户类型，tenantCode: {}", tenantCode);
            return UAPConstant.TENANT_TYPE_PERSONAL;
        }
    }

    @Override
    public void fillTenantExpirationInfo(Tenant tenant) {
        if (tenant == null || StringUtils.isBlank(tenant.getId())) {
            return;
        }

        try {
            String tenantId = tenant.getId();
            String tenantCode = tenant.getTenantCode();

            TenantExpirationDto dto = new TenantExpirationDto();
            // fillTenantExpirationInfo 用于填充租户列表信息，不需要检查用户是否在租户中
            // 所以这里不传loginName参数，使用null
            calculateAndFillExpirationInfo(dto, tenantId, tenantCode, null);

            // 填充到期信息到租户对象
            tenant.setExpirationDate(dto.getExpirationDate());
            tenant.setRemainingDays(dto.getRemainingDays());
            tenant.setIsExpired(dto.getIsExpired());
            tenant.setShouldAlert(dto.getShouldAlert());

        } catch (Exception e) {
            log.error("填充租户到期信息失败，tenantId: {}", tenant != null ? tenant.getId() : "null", e);
            // 发生异常时，设置默认值，不影响租户列表返回
            setDefaultExpirationInfo(tenant);
        }
    }

    /**
     * 计算并填充到期信息的核心逻辑（公共方法）
     * 根据租户ID和编码计算到期信息，并填充到DTO对象中
     *
     * @param dto 要填充的DTO对象（TenantExpirationDto或Tenant）
     * @param tenantId 租户ID
     * @param tenantCode 租户编码
     * @param loginName 用户登录名（用于检查用户是否在租户中。如果为null，则跳过用户检查）
     */
    private void calculateAndFillExpirationInfo(
            TenantExpirationDto dto, String tenantId, String tenantCode, String loginName) {
        try {
            // 判断租户类型
            String tenantType = determineTenantType(tenantCode);

            // 个人版和买断企业版不限期
            if (UAPConstant.TENANT_TYPE_PERSONAL.equals(tenantType)
                    || UAPConstant.TENANT_TYPE_ENTERPRISE_PURCHASED.equals(tenantType)) {
                setDefaultExpirationInfo(dto);
                return;
            }

            // 专业版和非买断企业版需要查询到期信息
            // 1. 先检查用户是否还在当前租户空间中（如果提供了loginName参数）
            if (StringUtils.isNotBlank(loginName)) {
                boolean hasSpace = checkTenantHasSpace(tenantId, loginName);
                if (!hasSpace) {
                    // 如果用户不在当前租户空间中，设置isExpired为true，表示空间不可用
                    log.debug("用户不在租户{}空间中，loginName: {}", tenantId, loginName);
                    dto.setExpirationDate(null);
                    dto.setRemainingDays(null);
                    dto.setIsExpired(true); // 不在空间中视为已到期
                    dto.setShouldAlert(false);
                    return;
                }
            }

            // 2. 租户拥有空间，查询到期信息（带缓存）
            TenantExpiration expiration = getTenantExpirationWithCache(tenantId);
            if (expiration == null) {
                // 如果没有到期信息，返回默认值
                log.debug("租户{}没有到期信息", tenantId);
                setDefaultExpirationInfo(dto);
                return;
            }

            // 解析到期日期
            String expirationDateStr = expiration.getExpirationDate();
            if (StringUtils.isBlank(expirationDateStr)) {
                setDefaultExpirationInfo(dto);
                return;
            }

            // 尝试解密（解密函数内部会判断是否是日期格式，如果是日期格式则直接返回，否则解密）
            try {
                expirationDateStr = EncryptUtils.decrypt(expirationDateStr);
            } catch (Exception e) {
                log.error("解密租户到期时间失败，tenantId: {}", tenantId, e);
                setDefaultExpirationInfo(dto);
                return;
            }

            // 解析日期并计算剩余天数
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
            LocalDate expirationDate;
            try {
                expirationDate = LocalDate.parse(expirationDateStr, formatter);
            } catch (Exception e) {
                log.error("解析到期日期失败，tenantId: {}, expirationDate: {}", tenantId, expirationDateStr, e);
                setDefaultExpirationInfo(dto);
                return;
            }

            LocalDate now = LocalDate.now();
            long remainingDays = ChronoUnit.DAYS.between(now, expirationDate);
            boolean isExpired = remainingDays < 0;
            boolean shouldAlert = remainingDays >= 0 && remainingDays <= alertDays;

            // 填充到期信息
            dto.setExpirationDate(expirationDateStr);
            dto.setRemainingDays(remainingDays);
            dto.setIsExpired(isExpired);
            dto.setShouldAlert(shouldAlert);

        } catch (Exception e) {
            log.error("计算租户到期信息失败，tenantId: {}", tenantId, e);
            setDefaultExpirationInfo(dto);
        }
    }

    /**
     * 检查用户是否还在当前租户空间中（带缓存）
     * 通过调用ClientAuthenticationAPI.getTenantListInAppByLoginName来判断用户是否还在租户中
     *
     * @param tenantId 租户ID
     * @param loginName 用户登录名
     * @return true表示用户在租户空间中，false表示用户不在租户空间中
     */
    private boolean checkTenantHasSpace(String tenantId, String loginName) {
        try {
            if (StringUtils.isBlank(loginName)) {
                log.warn("登录名为空，无法检查用户是否在租户空间中");
                // 登录名为空时，为了安全起见，假设不在空间中
                return false;
            }

            // 缓存key使用loginName和tenantId，因为不同用户对同一租户的访问权限可能不同
            String redisKey = REDIS_KEY_TENANT_HAS_SPACE_PREFIX + loginName + ":" + tenantId;

            // 先从Redis缓存中获取（缓存时间2小时）
            Object cache = RedisUtils.get(redisKey);
            if (cache != null && StringUtils.isNotBlank(cache.toString())) {
                String cacheStr = cache.toString();
                // 如果是空值标记，说明之前查询过且用户不在空间中，直接返回false
                if ("false".equals(cacheStr)) {
                    log.debug("从 Redis 缓存获取到用户不在租户空间中，loginName: {}，tenantId: {}", loginName, tenantId);
                    return false;
                } else if ("true".equals(cacheStr)) {
                    log.debug("从 Redis 缓存获取到用户在租户空间中，loginName: {}，tenantId: {}", loginName, tenantId);
                    return true;
                }
            }

            // 如果Redis中没有，调用UAP API查询用户所属的租户列表
            List<UapTenant> tenantList = ClientAuthenticationAPI.getTenantListInAppByLoginName(loginName);
            if (CollectionUtils.isEmpty(tenantList)) {
                log.warn("用户没有租户信息，loginName: {}", loginName);
                // 缓存结果（2小时）
                try {
                    RedisUtils.set(redisKey, "false", TENANT_SPACE_EMPTY_CACHE_EXPIRE_SECONDS);
                } catch (Exception e) {
                    log.warn("存入 Redis 缓存失败，loginName: {}，tenantId: {}", loginName, tenantId, e);
                }
                return false;
            }

            // 检查当前租户ID是否在用户所属的租户列表中
            boolean hasSpace = tenantList.stream().anyMatch(tenant -> tenantId.equals(tenant.getId()));

            // 查询到结果后存入Redis缓存（2小时）
            try {
                RedisUtils.set(redisKey, hasSpace ? "true" : "false", TENANT_SPACE_CACHE_EXPIRE_SECONDS);
                log.debug(
                        "用户租户空间拥有状态已存入 Redis 缓存，loginName: {}，tenantId: {}，hasSpace: {}",
                        loginName,
                        tenantId,
                        hasSpace);
            } catch (Exception e) {
                log.warn("存入 Redis 缓存失败，loginName: {}，tenantId: {}", loginName, tenantId, e);
            }

            return hasSpace;

        } catch (Exception e) {
            log.error("检查用户是否在租户空间中失败，tenantId: {}", tenantId, e);
            // 检查失败时，为了安全起见，假设不在空间中，阻止访问
            return false;
        }
    }

    /**
     * 获取租户到期信息（带缓存）
     *
     * @param tenantId 租户ID
     * @return 租户到期信息，如果不存在返回null
     */
    private TenantExpiration getTenantExpirationWithCache(String tenantId) {
        try {
            String redisKey = REDIS_KEY_TENANT_EXPIRATION_PREFIX + tenantId;
            TenantExpiration expiration = null;
            boolean fromCache = false;

            // 先从 Redis 缓存中获取
            try {
                Object cache = RedisUtils.get(redisKey);
                if (cache != null && StringUtils.isNotBlank(cache.toString())) {
                    String cacheStr = cache.toString();
                    // 如果是空值标记，说明之前查询过数据库且没有数据，直接返回null
                    if ("{}".equals(cacheStr)) {
                        log.debug("从 Redis 缓存获取到空值标记，tenantId: {}", tenantId);
                        return null;
                    } else {
                        ObjectMapper objectMapper = new ObjectMapper();
                        expiration = objectMapper.readValue(cacheStr, TenantExpiration.class);
                        fromCache = true;
                        log.debug("从 Redis 缓存获取租户到期信息，tenantId: {}", tenantId);
                    }
                }
            } catch (Exception e) {
                log.warn("从 Redis 读取租户到期信息失败，tenantId: {}，将查询数据库", tenantId, e);
            }

            // 如果 Redis 中没有，查询数据库
            if (!fromCache) {
                expiration = tenantExpirationDao.queryByTenantId(tenantId);

                // 查询到数据后存入 Redis 缓存（2小时，作为兜底机制）
                // 注意：如果后续有更新到期信息的接口，建议在更新时主动删除缓存
                if (expiration != null) {
                    try {
                        ObjectMapper objectMapper = new ObjectMapper();
                        String expirationJson = objectMapper.writeValueAsString(expiration);
                        RedisUtils.set(redisKey, expirationJson, TENANT_SPACE_CACHE_EXPIRE_SECONDS);
                        log.debug("租户到期信息已存入 Redis 缓存，tenantId: {}", tenantId);
                    } catch (Exception e) {
                        log.warn("存入 Redis 缓存失败，tenantId: {}", tenantId, e);
                    }
                } else {
                    // 如果没有到期信息，也缓存一个空值标记，避免频繁查询数据库（2小时）
                    try {
                        RedisUtils.set(redisKey, "{}", TENANT_SPACE_EMPTY_CACHE_EXPIRE_SECONDS);
                    } catch (Exception e) {
                        log.warn("存入 Redis 空值标记失败，tenantId: {}", tenantId, e);
                    }
                }
            }

            return expiration;

        } catch (Exception e) {
            log.error("获取租户到期信息失败，tenantId: {}", tenantId, e);
            // 失败时返回null，让调用方处理
            return null;
        }
    }

    /**
     * 设置默认的到期信息到DTO（用于异常情况）
     *
     * @param dto DTO对象
     */
    private void setDefaultExpirationInfo(TenantExpirationDto dto) {
        if (dto != null) {
            dto.setExpirationDate(null);
            dto.setRemainingDays(null);
            dto.setIsExpired(false);
            dto.setShouldAlert(false);
        }
    }

    /**
     * 设置默认的到期信息到Tenant对象（用于异常情况）
     *
     * @param tenant 租户对象
     */
    private void setDefaultExpirationInfo(Tenant tenant) {
        if (tenant != null) {
            tenant.setExpirationDate(null);
            tenant.setRemainingDays(null);
            tenant.setIsExpired(false);
            tenant.setShouldAlert(false);
        }
    }
}
