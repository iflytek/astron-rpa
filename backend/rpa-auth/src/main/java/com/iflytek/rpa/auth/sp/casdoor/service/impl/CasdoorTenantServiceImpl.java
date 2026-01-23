package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.TenantService;
import com.iflytek.rpa.auth.sp.casdoor.dao.CasdoorTenantDao;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorOrganizationMapper;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorTenantMapper;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorGroupExtendService;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorUserExtendService;
import com.iflytek.rpa.auth.sp.casdoor.utils.SessionUserUtils;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.entity.Organization;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.OrganizationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/12/10 17:28
 */
@Slf4j
@Service("casdoorTenantService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorTenantServiceImpl implements TenantService {

    @Autowired
    private OrganizationService organizationService;

    @Autowired
    private CasdoorGroupExtendService casdoorGroupExtendService;

    @Autowired
    private CasdoorTenantMapper casdoorTenantMapper;

    @Autowired
    private CasdoorOrganizationMapper casdoorOrganizationMapper;

    @Autowired
    private CasdoorUserExtendService casdoorUserExtendService;

    @Autowired
    private CasdoorTenantDao casdoorTenantDao;

    @Value("${casdoor.database.name:casdoor}")
    private String databaseName;

    /**
     * 租户下所有用户
     * @param userName 组织名称（organizationName）
     * @return 用户列表
     * @throws Exception 异常
     */
    @Override
    public AppResponse<List<UserVo>> getAllUser(String userName) throws Exception {

        try {
            log.debug("开始查询租户下所有用户，organizationName: {}", userName);

            // 参数校验
            if (Objects.isNull(userName) || userName.trim().isEmpty()) {
                log.warn("查询租户下所有用户失败：组织名称为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "组织名称不能为空");
            }

            // 查询用户列表
            List<User> users = casdoorUserExtendService.getUsers(userName);
            if (CollectionUtils.isEmpty(users)) {
                log.debug("组织下没有用户，organizationName: {}", userName);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个用户，organizationName: {}", users.size(), userName);

            // 转换为UserVo列表，过滤掉转换失败的对象
            List<UserVo> userVoList = users.stream()
                    .filter(user -> user != null)
                    .map(user -> {
                        try {
                            UserVo userVo = new UserVo();
                            userVo.setUserId(user.id);
                            userVo.setUserPhone(user.phone);
                            userVo.setUserName(user.name);
                            return userVo;
                        } catch (Exception e) {
                            log.warn(
                                    "用户信息转换失败，userId: {}, organizationName: {}",
                                    user != null ? user.id : "null",
                                    userName,
                                    e);
                            return null;
                        }
                    })
                    .filter(userVo -> userVo != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个用户，organizationName: {}", userVoList.size(), userName);
            return AppResponse.success(userVoList);
        } catch (IOException e) {
            log.error("查询租户下所有用户失败，organizationName: {}", userName, e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询租户下所有用户失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("查询租户下所有用户异常，organizationName: {}", userName, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询租户下所有用户异常: " + e.getMessage());
        }
    }

    /**
     * 当前登录用户在此应用的租户列表
     * @param request HTTP请求
     * @return 租户列表
     */
    @Override
    public AppResponse<List<Tenant>> getTenantListInApp(HttpServletRequest request) {
        try {
            log.debug("查询当前登录用户在此应用的租户列表（Casdoor暂不支持此功能，返回空列表）");
            return AppResponse.success(Collections.emptyList());
        } catch (Exception e) {
            log.error("查询当前登录用户在此应用的租户列表异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询当前登录用户在此应用的租户列表失败: " + e.getMessage());
        }
    }

    /**
     * 企业信息查询
     * @param request HTTP请求
     * @return 企业信息
     * @throws Exception 异常
     */
    @Override
    public AppResponse<TenantInfoDto> getTenantInfo(HttpServletRequest request) throws Exception {
        try {
            log.debug("开始查询企业信息");

            // 1. 获取当前租户ID
            User user = SessionUserUtils.getUserFromSession(request);
            if (user == null) {
                log.warn("查询企业信息失败：用户未登录");
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }

            if (user.owner == null || user.owner.isEmpty()) {
                log.warn("查询企业信息失败：租户ID为空");
                return AppResponse.error(ErrorCodeEnum.E_SERVICE_INFO_LOSE, "租户ID为空");
            }

            String tenantId = user.owner;
            log.debug("获取到租户ID: {}", tenantId);

            // 2. 查询Casdoor组织信息
            Organization organization = organizationService.getOrganization(tenantId);
            if (Objects.isNull(organization)) {
                log.warn("未查询到组织信息，tenantId: {}", tenantId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "未查询到组织信息");
            }

            // 3. 使用mapper转换为Tenant
            Tenant tenant = casdoorTenantMapper.toCommonTenant(organization);
            if (Objects.isNull(tenant)) {
                log.warn("组织信息转换失败，tenantId: {}", tenantId);
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "组织信息转换失败");
            }

            log.debug("租户信息转换成功，tenantId: {}, tenantName: {}", tenantId, tenant.getName());

            // 4. 从Tenant转换为TenantInfoDto
            TenantInfoDto tenantInfoDto = new TenantInfoDto();
            tenantInfoDto.setId(tenant.getId());
            tenantInfoDto.setName(tenant.getName());
            tenantInfoDto.setCode(tenant.getTenantCode());

            // TODO: 补充查询管理员详细信息，目前暂时都是admin（casdoor内置父租户）
            if (organization.owner != null && !organization.owner.isEmpty()) {
                tenantInfoDto.setManagerId(organization.owner);
                // 暂时使用owner作为managerName，后续可以根据需要查询用户详细信息
                tenantInfoDto.setManagerName(organization.owner);
            }

            log.debug("企业信息查询成功，tenantId: {}, tenantName: {}", tenantId, tenantInfoDto.getName());
            return AppResponse.success(tenantInfoDto);
        } catch (IOException e) {
            log.error("查询企业信息失败", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询企业信息失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("查询企业信息异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询企业信息异常: " + e.getMessage());
        }
    }

    /**
     * 获取租户ID
     * @param request HTTP请求
     * @return 租户ID
     */
    @Override
    public AppResponse<String> getTenantId(HttpServletRequest request) {
        try {
            // 从session获取当前用户
            User user = SessionUserUtils.getUserFromSession(request);

            if (user != null) {
                if (user.owner != null && !user.owner.isEmpty()) {
                    return AppResponse.success(user.owner);
                } else {
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE_INFO_LOSE, "租户ID为空");
                }
            } else {
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }
        } catch (Exception e) {
            log.error("获取租户ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户ID失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前登录的租户ID
     * @param request HTTP请求
     * @return 当前登录的租户ID
     */
    @Override
    public AppResponse<String> getCurrentTenantId(HttpServletRequest request) {
        return getTenantId(request);
    }

    /**
     * 获取当前登录的租户名称(同ID)
     * @param request HTTP请求
     * @return 当前登录的租户名称
     */
    @Override
    public AppResponse<String> getCurrentTenantName(HttpServletRequest request) {
        return getTenantId(request);
    }

    /**
     * 根据租户ID查询租户信息
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 租户信息
     */
    @Override
    public AppResponse<Tenant> queryTenantInfoById(String tenantId, HttpServletRequest request) {
        try {
            // 参数校验
            if (Objects.isNull(tenantId) || tenantId.trim().isEmpty()) {
                log.warn("查询租户信息失败：租户ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }

            log.debug("开始查询租户信息，tenantId: {}", tenantId);

            // 查询Casdoor组织信息
            Organization organization = organizationService.getOrganization(tenantId);
            if (Objects.isNull(organization)) {
                log.warn("未查询到组织信息，tenantId: {}", tenantId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "未查询到组织信息");
            }

            // 转换为通用租户对象
            Tenant commonTenant = casdoorTenantMapper.toCommonTenant(organization);
            if (Objects.isNull(commonTenant)) {
                log.warn("组织信息转换失败，tenantId: {}", tenantId);
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "组织信息转换失败");
            }

            log.debug("查询租户信息成功，tenantId: {}, tenantName: {}", tenantId, commonTenant.getName());
            return AppResponse.success(commonTenant);
        } catch (IOException e) {
            log.error("查询租户信息失败，tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询租户信息失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("查询租户信息异常，tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询租户信息异常: " + e.getMessage());
        }
    }

    /**
     * 更改企业管理员（暂不支持）
     * @param id 管理员ID
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> changeManager(String id, HttpServletRequest request) {
        try {
            log.debug("更改企业管理员，id: {}（Casdoor暂不支持此功能，返回提示信息）", id);
            return AppResponse.success("Casdoor暂不支持更改企业管理员功能");
        } catch (Exception e) {
            log.error("更改企业管理员异常，id: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "更改企业管理员失败: " + e.getMessage());
        }
    }

    /**
     * 根据租户id获取所有组织列表
     * @param tenantId 租户ID
     * @param request HTTP请求
     * @return 组织列表
     */
    @Override
    public AppResponse<List<Org>> getAllOrgList(String tenantId, HttpServletRequest request) {
        try {
            // 参数校验
            if (Objects.isNull(tenantId) || tenantId.trim().isEmpty()) {
                log.warn("获取组织列表失败：租户ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空");
            }

            log.debug("开始获取组织列表，tenantId: {}", tenantId);

            // 查询Casdoor组列表
            List<Group> groups = casdoorGroupExtendService.getGroups(tenantId);
            if (CollectionUtils.isEmpty(groups)) {
                log.debug("租户下没有组织，tenantId: {}", tenantId);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个组织，tenantId: {}", groups.size(), tenantId);

            // 转换为通用组织对象列表，过滤掉转换失败的对象
            List<Org> orgList = groups.stream()
                    .map(casdoorOrganizationMapper::toCommonOrg)
                    .filter(org -> org != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个组织，tenantId: {}", orgList.size(), tenantId);
            return AppResponse.success(orgList);
        } catch (IOException e) {
            log.error("获取组织列表失败，tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "获取组织列表失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("获取组织列表异常，tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取组织列表异常: " + e.getMessage());
        }
    }

    /**
     * 切换租户（暂不支持）
     * @param tenantId 切换租户id
     * @param request HTTP请求
     * @return 切换结果
     */
    @Override
    public AppResponse<String> switchTenant(String tenantId, HttpServletRequest request) {
        try {
            log.debug("切换租户，tenantId: {}（Casdoor暂不支持此功能，返回提示信息）", tenantId);
            return AppResponse.success("Casdoor暂不支持切换租户功能");
        } catch (Exception e) {
            log.error("切换租户异常，tenantId: {}", tenantId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "切换租户失败: " + e.getMessage());
        }
    }

    /**
     * 根据手机号查询用户所属的租户列表
     * @param organizationName 组织名
     * @param request HTTP请求
     * @return 租户列表
     */
    @Override
    public AppResponse<List<Tenant>> getTenantList(String organizationName, HttpServletRequest request) {
        try {
            Organization organization = organizationService.getOrganization(organizationName);
            Tenant tenant = casdoorTenantMapper.toCommonTenant(organization);
            return AppResponse.success(Collections.singletonList(tenant));

        } catch (Exception e) {
            log.error("获取组织异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取租户列表失败：" + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<String>> getAllTenantId() {
        // Casdoor模式下暂不支持此功能，返回空列表
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<List<String>> getTenantManagerIds(String tenantId) {
        // Casdoor模式下暂不支持此功能，返回空列表
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<List<String>> getTenantNormalUserIds(String tenantId) {
        // Casdoor模式下暂不支持此功能，返回空列表
        return AppResponse.success(Collections.emptyList());
    }

    @Override
    public AppResponse<List<String>> getNoClassifyTenantIds() {
        try {
            List<String> tenantIds = casdoorTenantDao.getNoClassifyTenantIds(databaseName);
            return AppResponse.success(tenantIds);
        } catch (Exception e) {
            log.error("获取未分类租户id失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取未分类租户id失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<Integer> updateTenantClassifyCompleted(List<String> ids) {
        // Casdoor模式下暂不支持此功能，返回成功但更新数量为1
        return AppResponse.success(1);
    }

    @Override
    public AppResponse<List<String>> getAllEnterpriseTenantId() {
        return AppResponse.success(new ArrayList<>());
    }

    @Override
    public AppResponse<Integer> getTenantUserType(String userId, String tenantId) {
        // 默认返回普通用户
        return AppResponse.success(2);
    }

    @Override
    public AppResponse<TenantExpirationDto> getTenantExpiration(HttpServletRequest request) {
        // Casdoor模式下暂不支持此功能，返回默认的不限期租户信息
        TenantExpirationDto dto = new TenantExpirationDto();
        dto.setTenantType("personal"); // 默认个人版
        // 获取当前登录用户的租户id
        String tenantId = SessionUserUtils.getTenantOwnerFromSession(request);
        dto.setTenantId(tenantId);
        dto.setExpirationDate(null); // 不限期
        dto.setRemainingDays(null); // 不限期
        dto.setIsExpired(false); // 不限期
        dto.setShouldAlert(false); // 不限期
        return AppResponse.success(dto);
    }

    @Override
    public boolean checkSpaceExpired(HttpServletRequest request) {
        // Casdoor模式下暂不支持此功能，默认返回未过期
        return false;
    }

    @Override
    public void fillTenantExpirationInfo(Tenant tenant) {
        // Casdoor模式下暂不支持此功能，不填充任何信息
    }
}
