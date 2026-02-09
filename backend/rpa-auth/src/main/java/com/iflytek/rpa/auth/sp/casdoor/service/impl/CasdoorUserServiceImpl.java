package com.iflytek.rpa.auth.sp.casdoor.service.impl;

import cn.hutool.core.collection.CollUtil;
import cn.hutool.core.collection.CollectionUtil;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.auth.core.entity.*;
import com.iflytek.rpa.auth.core.service.UserService;
import com.iflytek.rpa.auth.sp.casdoor.dao.CasdoorGroupDao;
import com.iflytek.rpa.auth.sp.casdoor.dao.CasdoorUserDao;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorLoginResult;
import com.iflytek.rpa.auth.sp.casdoor.entity.CasdoorSignupDto;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorOrganizationMapper;
import com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorUserMapper;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorAuthExtendService;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorGroupExtendService;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorLoginExtendService;
import com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorUserExtendService;
import com.iflytek.rpa.auth.sp.casdoor.utils.SessionUserUtils;
import com.iflytek.rpa.auth.sp.casdoor.utils.TokenManager;
import com.iflytek.rpa.auth.utils.AppResponse;
import com.iflytek.rpa.auth.utils.ErrorCodeEnum;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.casbin.casdoor.entity.Group;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.RoleService;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

@Slf4j
@Service("casdoorUserService")
@ConditionalOnProperty(name = "rpa.auth.deployment-mode", havingValue = "casdoor", matchIfMissing = true)
public class CasdoorUserServiceImpl implements UserService {

    @Autowired
    private org.casbin.casdoor.service.UserService userService;

    @Autowired
    private CasdoorUserExtendService userExtendService;

    @Autowired
    private RoleService roleService;

    @Autowired
    private CasdoorUserMapper userMapper;

    @Autowired
    private com.iflytek.rpa.auth.sp.casdoor.mapper.CasdoorPermissionMapper permissionMapper;

    @Autowired
    private CasdoorOrganizationMapper organizationMapper;

    @Value("${casdoor.database.name:casdoor}")
    private String databaseName;

    @Autowired
    private CasdoorUserDao casdoorUserDao;

    @Autowired
    private CasdoorGroupDao casdoorGroupDao;

    @Autowired
    private CasdoorAuthExtendService casdoorAuthExtendService;

    @Autowired
    private CasdoorLoginExtendService casdoorLoginExtendService;

    @Value("${casdoor.organization-name}")
    private String organizationName;

    @Value("${casdoor.application-name}")
    private String applicationName;

    @Value("${casdoor.external-endpoint:}")
    private String externalEndPoint;

    @Value("${casdoor.redirect-url:}")
    private String redirectUrl;

    @Value("${casdoor.certificate:}")
    private String certificate;

    @Autowired
    private CasdoorGroupExtendService casdoorGroupExtendService;

    @Autowired
    private com.iflytek.rpa.auth.sp.casdoor.service.extend.CasdoorAccountExtendService casdoorAccountExtendService;

    /**
     * 注册
     * @param registerDto 注册信息
     * @param request HTTP请求
     * @return 注册结果
     */
    @Override
    public AppResponse<String> register(RegisterDto registerDto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始用户注册");

            // 参数校验
            if (registerDto == null) {
                log.warn("用户注册失败：注册参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "注册参数不能为空");
            }

            if (StringUtils.isBlank(registerDto.getPassword())) {
                log.warn("用户注册失败：密码为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "密码不能为空");
            }

            // 验证两次密码是否一致
            if (!StringUtils.equals(registerDto.getPassword(), registerDto.getConfirmPassword())) {
                log.warn("用户注册失败：两次输入的密码不一致");
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "两次输入的密码不一致");
            }

            String phone = registerDto.getPhone().trim();
            String loginName = registerDto.getLoginName();
            log.debug("用户注册参数，手机号: {}, 登录名: {}", phone, loginName);

            // 如果没有提供登录名，使用手机号作为登录名
            String username = StringUtils.isNotBlank(loginName) ? loginName.trim() : phone;
            log.debug("确定用户名为: {}", username);

            // 构建Casdoor注册请求
            CasdoorSignupDto casdoorSignupDto = new CasdoorSignupDto();
            casdoorSignupDto.setApplication(applicationName);
            casdoorSignupDto.setOrganization(organizationName);
            casdoorSignupDto.setUsername(username);
            casdoorSignupDto.setName(username);
            casdoorSignupDto.setPassword(registerDto.getPassword());

            // 调用Casdoor注册接口
            log.debug("调用Casdoor API注册用户，username: {}", username);
            CasdoorLoginResult signupResult = casdoorLoginExtendService.signup(casdoorSignupDto);

            if (signupResult == null) {
                log.error("用户注册失败：Casdoor API返回为空，username: {}", username);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "用户注册失败：API返回为空");
            }

            if (StringUtils.isBlank(signupResult.getUserId())) {
                log.error("用户注册失败：未获取到用户ID，username: {}", username);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "用户注册失败：未获取到用户ID");
            }

            String userId = signupResult.getUserId();
            log.debug("用户注册成功，userId: {}, username: {}, phone: {}", userId, username, phone);
            return AppResponse.success(userId);
        } catch (IOException e) {
            log.error("用户注册失败（IO异常）", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "用户注册失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("用户注册异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户注册异常: " + e.getMessage());
        }
    }

    /**
     * 按名称模糊搜索所有员工或部门
     * @param name 搜索关键字
     * @param request HTTP请求
     * @return 搜索结果
     */
    @Override
    public AppResponse<GetDeptOrUserDto> searchDeptOrUser(String name, HttpServletRequest request) {
        try {
            log.debug("开始按名称模糊搜索员工或部门，name: {}", name);

            // 参数校验
            if (name == null || name.trim().isEmpty()) {
                log.warn("按名称模糊搜索员工或部门失败：搜索关键字为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "搜索关键字不能为空");
            }

            // 获取当前租户ID（owner），用于限定查询范围
            String owner = getCurrentTenantOwner(request);

            // 查询用户（限定在当前租户下，如果owner为空则查询全部）
            List<User> users = casdoorUserDao.searchUserByName(name, owner, databaseName);
            if (users == null) {
                users = Collections.emptyList();
            }
            log.debug("查询到 {} 个用户，name: {}", users.size(), name);

            // 转换为通用用户对象列表，过滤掉转换失败的对象
            List<com.iflytek.rpa.auth.core.entity.User> commonUserList = users.stream()
                    .filter(user -> user != null)
                    .map(user -> {
                        try {
                            return userMapper.toCommonUser(user);
                        } catch (Exception e) {
                            log.warn("用户信息转换失败，userId: {}, name: {}", user != null ? user.id : "null", name, e);
                            return null;
                        }
                    })
                    .filter(user -> user != null)
                    .collect(Collectors.toList());
            log.debug("成功转换 {} 个用户，name: {}", commonUserList.size(), name);

            // 查询部门（在casdoor中对应group，限定在当前租户下，如果owner为空则查询全部）
            List<Group> groups = casdoorGroupDao.searchDeptByName(name, owner, databaseName);
            if (groups == null) {
                groups = Collections.emptyList();
            }
            log.debug("查询到 {} 个部门，name: {}", groups.size(), name);

            // 转换为通用部门对象列表，过滤掉转换失败的对象
            List<Org> commonOrgList = groups.stream()
                    .filter(group -> group != null)
                    .map(group -> {
                        try {
                            return organizationMapper.toCommonOrg(group);
                        } catch (Exception e) {
                            log.warn("部门信息转换失败，groupId: {}, name: {}", group != null ? group.name : "null", name, e);
                            return null;
                        }
                    })
                    .filter(org -> org != null)
                    .collect(Collectors.toList());
            log.debug("成功转换 {} 个部门，name: {}", commonOrgList.size(), name);

            // 组装到DTO
            GetDeptOrUserDto getDeptOrUserDto = new GetDeptOrUserDto();
            getDeptOrUserDto.setUserList(commonUserList);
            getDeptOrUserDto.setDeptList(commonOrgList);

            log.debug("按名称模糊搜索员工或部门成功，用户数: {}, 部门数: {}, name: {}", commonUserList.size(), commonOrgList.size(), name);
            return AppResponse.success(getDeptOrUserDto);
        } catch (Exception e) {
            log.error("按名称模糊搜索员工或部门异常，name: {}", name, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "按名称模糊搜索员工或部门失败: " + e.getMessage());
        }
    }

    /**
     * 编辑员工
     * @param updateUapUserDto 更新员工信息
     * @param request HTTP请求
     * @return 编辑结果
     */
    @Override
    public AppResponse<String> editUser(UpdateUapUserDto updateUapUserDto, HttpServletRequest request)
            throws IOException {
        try {
            log.debug(
                    "开始编辑员工，userId: {}",
                    updateUapUserDto.getUser() != null
                            ? updateUapUserDto.getUser().getId()
                            : "null");

            // 参数校验
            if (updateUapUserDto == null || updateUapUserDto.getUser() == null) {
                log.warn("编辑员工失败：参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "更新用户信息不能为空");
            }

            UpdateUserDto updateUserDto = updateUapUserDto.getUser();
            if (updateUserDto.getId() == null || updateUserDto.getId().trim().isEmpty()) {
                log.warn("编辑员工失败：用户ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "用户ID不能为空");
            }

            // 先查询现有用户信息，保留一些默认值
            User existingUser = null;
            try {
                existingUser = userExtendService.getUserById(updateUserDto.getId());
            } catch (Exception e) {
                log.warn("查询现有用户信息失败，userId: {}", updateUserDto.getId(), e);
            }

            // 核心信息转换到Casdoor User实体，注：拓展信息目前不支持转换
            User userToUpdate = convertUpdateUserDtoToCasdoorUser(updateUserDto, existingUser, request);

            // 更新用户
            log.debug("调用Casdoor API更新用户，userId: {}", userToUpdate.id);
            CasdoorResponse<String, Object> updateUserResponse = userExtendService.updateUser(userToUpdate);

            if (updateUserResponse == null) {
                log.error("更新用户失败：Casdoor API返回为空，userId: {}", userToUpdate.id);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "更新用户失败：API返回为空");
            }

            if (updateUserResponse.getStatus() != null && !"ok".equals(updateUserResponse.getStatus())) {
                log.error(
                        "更新用户失败：Casdoor API返回错误，userId: {}, status: {}, msg: {}",
                        userToUpdate.id,
                        updateUserResponse.getStatus(),
                        updateUserResponse.getMsg());
                return AppResponse.error(
                        ErrorCodeEnum.E_API_EXCEPTION,
                        "更新用户失败: " + (updateUserResponse.getMsg() != null ? updateUserResponse.getMsg() : "未知错误"));
            }

            log.debug("更新用户成功，userId: {}", userToUpdate.id);
            return AppResponse.success("更新用户成功");
        } catch (IOException e) {
            log.error("编辑员工失败", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "编辑员工失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("编辑员工异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "编辑员工异常: " + e.getMessage());
        }
    }

    /**
     * 将UpdateUserDto转换为Casdoor User实体(更新用户服务使用)
     * 注：拓展信息目前不支持转换
     *
     * @param updateUserDto 更新用户DTO
     * @param existingUser 现有用户信息（用于保留未更新的字段）
     * @param request HTTP请求（用于从session获取租户ID）
     * @return Casdoor User实体
     */
    private User convertUpdateUserDtoToCasdoorUser(
            UpdateUserDto updateUserDto, User existingUser, HttpServletRequest request) {
        User userToUpdate = new User();

        // 基本字段映射
        userToUpdate.id = updateUserDto.getId();
        userToUpdate.name = updateUserDto.getLoginName() != null
                ? updateUserDto.getLoginName()
                : (existingUser != null ? existingUser.name : "");
        userToUpdate.displayName = updateUserDto.getName() != null
                ? updateUserDto.getName()
                : (existingUser != null ? existingUser.displayName : "");
        userToUpdate.phone = updateUserDto.getPhone() != null
                ? updateUserDto.getPhone()
                : (existingUser != null ? existingUser.phone : "");
        userToUpdate.email = updateUserDto.getEmail() != null
                ? updateUserDto.getEmail()
                : (existingUser != null ? existingUser.email : null);

        // 用户类型转换：userType -> isAdmin, isGlobalAdmin
        // SUPER_ADMIN(1), SYSTEM_ADMIN(2), NORMAL_USER(-1), RESOURCE_POOL_USER(3), TENANT_SUPER_ADMIN(0)
        if (updateUserDto.getUserType() != null) {
            Integer userType = updateUserDto.getUserType();
            // SUPER_ADMIN(1) 或 TENANT_SUPER_ADMIN(0) 或 SYSTEM_ADMIN(2) 设置为管理员
            userToUpdate.isAdmin = (userType == 1 || userType == 0 || userType == 2);
            // SUPER_ADMIN(1) 设置为全局管理员
            userToUpdate.isGlobalAdmin = (userType == 1);
        } else if (existingUser != null) {
            userToUpdate.isAdmin = existingUser.isAdmin;
            userToUpdate.isGlobalAdmin = existingUser.isGlobalAdmin;
        }

        // 状态字段转换：status (0停用 -> isForbidden=true, 1启用 -> isForbidden=false)
        if (updateUserDto.getStatus() != null) {
            userToUpdate.isForbidden = (updateUserDto.getStatus() == 0);
        } else if (existingUser != null) {
            userToUpdate.isForbidden = existingUser.isForbidden;
        }

        // owner字段保持现有值（owner是租户ID，对应Casdoor的Organization，不能从orgId获取）
        // 注意：orgId对应的是Casdoor的Group，不是Organization，所以不能将orgId赋值给owner
        if (existingUser != null && existingUser.owner != null) {
            userToUpdate.owner = existingUser.owner;
        } else {
            // 如果没有现有用户信息，尝试从当前登录用户获取租户ID（owner）
            String owner = SessionUserUtils.getTenantOwnerFromSession(request);
            if (owner != null && !owner.trim().isEmpty()) {
                userToUpdate.owner = owner;
                log.debug("从当前登录用户获取租户ID（owner）: {}", owner);
            } else {
                log.warn("更新用户时owner为空，且无法从当前登录用户获取租户ID，可能会导致更新失败");
            }
        }

        // 地址字段转换：String -> String[]
        if (updateUserDto.getAddress() != null
                && !updateUserDto.getAddress().trim().isEmpty()) {
            String address = updateUserDto.getAddress().trim();
            if (address.contains(",")) {
                userToUpdate.address = Arrays.stream(address.split(","))
                        .map(String::trim)
                        .filter(s -> !s.isEmpty())
                        .toArray(String[]::new);
            } else {
                userToUpdate.address = new String[] {address};
            }
            userToUpdate.location = address;
        } else if (existingUser != null && existingUser.address != null) {
            userToUpdate.address = existingUser.address;
            userToUpdate.location = existingUser.location;
        }

        // 备注字段映射到bio
        if (updateUserDto.getRemark() != null
                && !updateUserDto.getRemark().trim().isEmpty()) {
            userToUpdate.bio = updateUserDto.getRemark();
        } else if (existingUser != null && existingUser.bio != null) {
            userToUpdate.bio = existingUser.bio;
        }

        // 身份证号映射
        if (updateUserDto.getIdNumber() != null
                && !updateUserDto.getIdNumber().trim().isEmpty()) {
            userToUpdate.idCard = updateUserDto.getIdNumber();
        } else if (existingUser != null && existingUser.idCard != null) {
            userToUpdate.idCard = existingUser.idCard;
        }

        // 生日字段转换：Date -> String (yyyy-MM-dd)
        if (updateUserDto.getBirthday() != null) {
            userToUpdate.birthday = formatDate(updateUserDto.getBirthday());
        } else if (existingUser != null && existingUser.birthday != null) {
            userToUpdate.birthday = existingUser.birthday;
        }

        // 保留现有用户的时间戳和其他字段
        if (existingUser != null) {
            userToUpdate.createdTime = existingUser.createdTime;
            userToUpdate.updatedTime = formatDateTime(new Date()); // 更新时间为当前时间
            userToUpdate.type = existingUser.type != null ? existingUser.type : "normal-user";
            userToUpdate.password = existingUser.password != null ? existingUser.password : "";
            userToUpdate.passwordSalt = existingUser.passwordSalt != null ? existingUser.passwordSalt : "";
            userToUpdate.isDeleted = existingUser.isDeleted;
            userToUpdate.emailVerified = existingUser.emailVerified;
            userToUpdate.properties = existingUser.properties;
            userToUpdate.roles = existingUser.roles;
            userToUpdate.permissions = existingUser.permissions;
        } else {
            // 如果查询不到现有用户，设置默认值
            userToUpdate.type = "normal-user";
            userToUpdate.password = "";
            userToUpdate.passwordSalt = "";
            userToUpdate.isDeleted = false;
            userToUpdate.emailVerified = false;
            userToUpdate.createdTime = formatDateTime(new Date());
            userToUpdate.updatedTime = formatDateTime(new Date());
        }

        return userToUpdate;
    }

    /**
     * 从当前登录用户获取租户ID（Casdoor中的 owner）
     *
     * @param request HTTP请求
     * @return 租户ID（owner），获取失败时返回null
     */
    private String getCurrentTenantOwner(HttpServletRequest request) {
        return SessionUserUtils.getTenantOwnerFromSession(request);
    }

    /**
     * 格式化Date对象为日期字符串 (yyyy-MM-dd)
     */
    private String formatDate(Date date) {
        if (date == null) {
            return "";
        }
        java.text.SimpleDateFormat formatter = new java.text.SimpleDateFormat("yyyy-MM-dd");
        return formatter.format(date);
    }

    /**
     * 格式化Date对象为日期时间字符串 (yyyy-MM-dd HH:mm:ss)
     */
    private String formatDateTime(Date date) {
        if (date == null) {
            return "";
        }
        java.text.SimpleDateFormat formatter = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return formatter.format(date);
    }

    /**
     * 新增员工
     * @param createUapUserDto 新增员工信息
     * @param request HTTP请求
     * @return 新增结果
     */
    @Override
    public AppResponse<String> addUser(CreateUapUserDto createUapUserDto, HttpServletRequest request)
            throws IOException {
        try {
            log.debug("开始新增员工");

            // 参数校验
            if (createUapUserDto == null || createUapUserDto.getUser() == null) {
                log.warn("新增员工失败：参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "新增用户信息不能为空");
            }

            CreateUserDto createUserDto = createUapUserDto.getUser();

            // 登录名必填
            if (createUserDto.getLoginName() == null
                    || createUserDto.getLoginName().trim().isEmpty()) {
                log.warn("新增员工失败：登录名为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "登录名不能为空");
            }

            // 校验用户是否已存在（根据登录名）
            try {
                User existingUserByName = userExtendService.getUser(createUserDto.getLoginName());
                if (existingUserByName != null) {
                    log.warn("新增员工失败：登录名已存在，loginName: {}", createUserDto.getLoginName());
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "登录名已存在");
                }
            } catch (Exception e) {
                // 用户不存在是正常的，继续执行
                log.debug("用户不存在（按登录名），loginName: {}", createUserDto.getLoginName());
            }

            // 获取当前租户ID（owner），注意：orgId对应的是Casdoor的Group，不是Organization（租户）
            // owner必须对应Casdoor的Organization name，不能使用orgId
            String owner = getCurrentTenantOwner(request);

            if (owner == null || owner.trim().isEmpty()) {
                log.warn("新增员工失败：租户ID为空，需要用户已登录才能获取当前租户ID");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "租户ID不能为空，请确保用户已登录");
            }

            log.debug("新增员工，loginName: {}, owner: {}", createUserDto.getLoginName(), owner);

            // 核心信息转换到Casdoor User实体，注：拓展信息目前不支持转换
            User userToAdd = convertCreateUserDtoToCasdoorUser(createUserDto, owner);

            // 添加用户
            log.debug("调用Casdoor API添加用户，loginName: {}", userToAdd.name);
            CasdoorResponse<String, Object> addUserResponse = userExtendService.addUser(userToAdd);

            if (addUserResponse == null) {
                log.error("添加用户失败：Casdoor API返回为空，loginName: {}", userToAdd.name);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "添加用户失败：API返回为空");
            }

            if (addUserResponse.getStatus() != null && !"ok".equals(addUserResponse.getStatus())) {
                log.error(
                        "添加用户失败：Casdoor API返回错误，loginName: {}, status: {}, msg: {}",
                        userToAdd.name,
                        addUserResponse.getStatus(),
                        addUserResponse.getMsg());
                return AppResponse.error(
                        ErrorCodeEnum.E_API_EXCEPTION,
                        "添加用户失败: " + (addUserResponse.getMsg() != null ? addUserResponse.getMsg() : "未知错误"));
            }

            log.debug("添加用户成功，loginName: {}", userToAdd.name);
            return AppResponse.success("添加用户成功");
        } catch (IOException e) {
            log.error("新增员工失败", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "新增员工失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("新增员工异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "新增员工异常: " + e.getMessage());
        }
    }

    /**
     * 将CreateUserDto转换为Casdoor User实体(新增用户服务使用)
     * 注：拓展信息目前不支持转换
     *
     * @param createUserDto 创建用户DTO
     * @param owner 租户ID（organization name）
     * @return Casdoor User实体
     */
    private User convertCreateUserDtoToCasdoorUser(CreateUserDto createUserDto, String owner) {
        User userToAdd = new User();

        // 设置owner和name（name为登录名）
        userToAdd.owner = owner;
        userToAdd.name = createUserDto.getLoginName() != null
                ? createUserDto.getLoginName().trim()
                : "";

        // 基本字段映射
        userToAdd.displayName = createUserDto.getName() != null ? createUserDto.getName() : "";
        userToAdd.phone = createUserDto.getPhone() != null ? createUserDto.getPhone() : "";
        userToAdd.email = createUserDto.getEmail();

        // 用户类型转换：userType -> isAdmin, isGlobalAdmin
        // SUPER_ADMIN(1), SYSTEM_ADMIN(2), NORMAL_USER(-1), RESOURCE_POOL_USER(3), TENANT_SUPER_ADMIN(0)
        if (createUserDto.getUserType() != null) {
            Integer userType = createUserDto.getUserType();
            // SUPER_ADMIN(1) 或 TENANT_SUPER_ADMIN(0) 或 SYSTEM_ADMIN(2) 设置为管理员
            userToAdd.isAdmin = (userType == 1 || userType == 0 || userType == 2);
            // SUPER_ADMIN(1) 设置为全局管理员
            userToAdd.isGlobalAdmin = (userType == 1);
        } else {
            // 默认值为普通用户
            userToAdd.isAdmin = false;
            userToAdd.isGlobalAdmin = false;
        }

        // 状态字段转换：status (0停用 -> isForbidden=true, 1启用 -> isForbidden=false)
        if (createUserDto.getStatus() != null) {
            userToAdd.isForbidden = (createUserDto.getStatus() == 0);
        } else {
            // 默认启用
            userToAdd.isForbidden = false;
        }

        // 地址字段转换：String -> String[]
        if (createUserDto.getAddress() != null
                && !createUserDto.getAddress().trim().isEmpty()) {
            String address = createUserDto.getAddress().trim();
            if (address.contains(",")) {
                userToAdd.address = Arrays.stream(address.split(","))
                        .map(String::trim)
                        .filter(s -> !s.isEmpty())
                        .toArray(String[]::new);
            } else {
                userToAdd.address = new String[] {address};
            }
            userToAdd.location = address;
        }

        // 备注字段映射到bio
        if (createUserDto.getRemark() != null
                && !createUserDto.getRemark().trim().isEmpty()) {
            userToAdd.bio = createUserDto.getRemark();
        }

        // 身份证号映射
        if (createUserDto.getIdNumber() != null
                && !createUserDto.getIdNumber().trim().isEmpty()) {
            userToAdd.idCard = createUserDto.getIdNumber();
        }

        // 生日字段转换：Date -> String (yyyy-MM-dd)
        if (createUserDto.getBirthday() != null) {
            userToAdd.birthday = formatDate(createUserDto.getBirthday());
        }

        // 设置默认值和新建时间
        userToAdd.type = "normal-user";
        userToAdd.password = ""; // 新建用户时密码为空，后续可能需要单独设置密码
        userToAdd.passwordSalt = "";
        userToAdd.isDeleted = false;
        userToAdd.emailVerified = false;
        userToAdd.createdTime = formatDateTime(new Date());
        userToAdd.updatedTime = formatDateTime(new Date());

        return userToAdd;
    }

    /**
     * 分页查询当前机构的用户
     * @param listUserDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    @Override
    public AppResponse<PageDto<DeptUserDto>> queryUserListByOrgId(ListUserDto listUserDto, HttpServletRequest request)
            throws IOException {
        // 查询参数queryMap，可选，默认按OrgId的机构（casdoor群组）过滤
        Map<String, String> queryMap = new HashMap<>();
        queryMap.put("groupName", listUserDto.getOrgId());
        // listUserDto中只用到了页数信息
        int pageNum = listUserDto.getPageNum() == null ? 1 : listUserDto.getPageNum();
        int pageSize = listUserDto.getPageSize() == null ? 100 : listUserDto.getPageSize();

        // 按页查询租户（casdoor的organization）下用户
        Map<String, Object> paginationUsers = userExtendService.getPaginationUsers(pageNum, pageSize, queryMap);
        List<User> userList = new ArrayList<>();
        if (!Objects.isNull(paginationUsers)) {
            // 收集deptUserDtoList
            userList = (List<User>) paginationUsers.getOrDefault("casdoorUsers", Collections.emptyList());
        }

        Long totalCount = ((Number) paginationUsers.getOrDefault("data2", 0)).longValue();
        List<DeptUserDto> deptUserDtoList = new ArrayList<>();

        for (User user : userList) {
            DeptUserDto deptUserDto = new DeptUserDto();
            com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(user);
            BeanUtils.copyProperties(commonUser, deptUserDto);
            // 按名称查询用户信息，拿到角色信息
            User userInfo = userExtendService.getUser(user.name);
            if (!CollectionUtils.isEmpty(userInfo.roles)) {
                if (userInfo.roles.size() > 1) {
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户存在多个绑定角色");
                }
                org.casbin.casdoor.entity.Role role = userInfo.roles.get(0);
                if (role != null) {
                    // 注：casdoor中角色没有id只有name
                    deptUserDto.setRoleId(role.name);
                    deptUserDto.setRoleName(role.name);
                }
            }

            deptUserDtoList.add(deptUserDto);
        }

        // 组装结果
        PageDto<DeptUserDto> deptUserPage = new PageDto<>();
        deptUserPage.setResult(deptUserDtoList);
        deptUserPage.setPageSize(pageSize);
        deptUserPage.setCurrentPageNo(pageNum);
        deptUserPage.setTotalCount(totalCount);
        return AppResponse.success(deptUserPage);
    }

    /**
     * 角色管理-根据部门id查询部门下的人员和子部门
     * @param id 部门ID
     * @param request HTTP请求
     * @return 部门和人员列表
     */
    @Override
    public AppResponse<List<CurrentDeptUserDto>> queryUserAndDept(String id, HttpServletRequest request) {
        try {
            log.debug("查询部门下的人员和子部门，id: {}（Casdoor暂不支持此功能，返回空列表）", id);
            return AppResponse.success(Collections.emptyList());
        } catch (Exception e) {
            log.error("查询部门下的人员和子部门异常，id: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询部门下的人员和子部门失败: " + e.getMessage());
        }
    }

    /**
     * 角色管理-根据名字或手机号模糊查询员工
     * @param keyWord 搜索关键字
     * @param request HTTP请求
     * @return 员工列表
     */
    @Override
    public AppResponse<List<CurrentDeptUserDto>> searchUserWithStatus(String keyWord, HttpServletRequest request)
            throws IOException {
        // 获取当前租户ID（owner），可选
        String owner = getCurrentTenantOwner(request);
        List<User> users = casdoorUserDao.searchUserByNameOrPhone(keyWord, owner, databaseName);
        List<CurrentDeptUserDto> currentDeptUserDtoList = new ArrayList<>();
        for (User user : users) {
            CurrentDeptUserDto currentDeptUserDto = new CurrentDeptUserDto();
            currentDeptUserDto.setId(user.id);
            currentDeptUserDto.setName(user.name + "(" + user.phone + ")");
            currentDeptUserDto.setType("user");
            User userInfo = userExtendService.getUser(user.name);
            if (!CollectionUtils.isEmpty(userInfo.roles)) {
                if (userInfo.roles.size() > 1) {
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "用户存在多个绑定角色");
                }
                org.casbin.casdoor.entity.Role role = userInfo.roles.get(0);
                currentDeptUserDto.setStatus(null != role);
            }
            currentDeptUserDtoList.add(currentDeptUserDto);
        }
        return AppResponse.success(currentDeptUserDtoList);
    }

    /**
     * 角色管理-添加成员
     * @param bindUserListDto 绑定用户列表信息
     * @param request HTTP请求
     * @return 绑定结果
     */
    @Override
    public AppResponse<String> bindUserListRole(BindUserListDto bindUserListDto, HttpServletRequest request)
            throws IOException {
        if (StringUtils.isBlank(bindUserListDto.getRoleId()) || CollUtil.isEmpty(bindUserListDto.getUserIds())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        List<String> userIds = bindUserListDto.getUserIds();

        // 先查出来完整role信息，构造需要更新角色的用户id集合，用于调用更新接口
        org.casbin.casdoor.entity.Role roleInfoToUpdate = roleService.getRole(bindUserListDto.getRoleId());
        Set<String> userSetOfTargetRole = new HashSet<>(Arrays.asList(roleInfoToUpdate.roles));
        // 查出来默认角色信息，构造需要删除默认角色的用户id集合，用于调用更新接口清除用户的默认角色
        org.casbin.casdoor.entity.Role defaultRoleInfo = roleService.getRole("example-role");
        Set<String> userSetOfDefaultRole = new HashSet<>(Arrays.asList(defaultRoleInfo.roles));

        // 遍历传入的用户id列表
        for (String userId : userIds) {
            // 根据id查询用户，获取用户绑定角色信息
            User userById = userExtendService.getUserById(userId);
            // 先查询用户是否有默认角色，如果有，先解绑默认角色
            String userIdForApi = userById.owner + "/" + userById.name;
            if (userSetOfDefaultRole.contains(userIdForApi)) {
                userSetOfDefaultRole.remove(userIdForApi);
            }
            // 添加到需要更新角色的用户id集合
            userSetOfTargetRole.add(userIdForApi);
        }

        // 更新目标角色和默认角色的user绑定信息
        roleInfoToUpdate.roles = userSetOfTargetRole.toArray(new String[0]);
        CasdoorResponse<String, Object> updateRoleTargetResponse = roleService.updateRole(roleInfoToUpdate);
        defaultRoleInfo.roles = userSetOfDefaultRole.toArray(new String[0]);
        CasdoorResponse<String, Object> updateRoleDefaultResponse = roleService.updateRole(defaultRoleInfo);

        return AppResponse.success("绑定角色成功");
    }

    /**
     * 人员解绑角色
     * @param bindRoleDto 解绑角色信息
     * @param request HTTP请求
     * @return 解绑结果
     */
    @Override
    public AppResponse<String> unbindRole(BindRoleDto bindRoleDto, HttpServletRequest request) throws IOException {
        List<String> roleIdList = bindRoleDto.getRoleIdList();
        // 根据id查询出用户的详细信息，用于合成casdoor可识别的id（owner/name）
        User targetUser = userExtendService.getUser(bindRoleDto.getUserId());
        String idForApi = targetUser.owner + "/" + targetUser.name;
        // 查询每个角色的角色详细信息，获取原始users，从中丢掉目标用户，再次更新角色信息。（casdoor的角色解绑是以角色为主体的）
        for (String roleId : roleIdList) {
            org.casbin.casdoor.entity.Role role = roleService.getRole(roleId);
            List<String> usersToUpdate = new ArrayList<>();
            for (String userId : role.users) {
                if (!StringUtils.equals(userId, idForApi)) {
                    usersToUpdate.add(userId);
                }
            }
            role.users = usersToUpdate.toArray(new String[0]);
            CasdoorResponse<String, Object> updateRoleCasdoorResponse = roleService.updateRole(role);
        }
        return AppResponse.success("解绑角色成功");
    }

    /**
     * 分页获取角色绑定的用户列表，可根据登录名或姓名模糊查询（casdoor不支持分页查角色下的用户列表，手动分页）
     * @param listUserByRoleDto 查询条件
     * @param request HTTP请求
     * @return 分页用户列表
     */
    @Override
    public AppResponse<PageDto<com.iflytek.rpa.auth.core.entity.User>> queryBindListByRole(
            ListUserByRoleDto listUserByRoleDto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始分页获取角色绑定的用户列表，roleId: {}", listUserByRoleDto != null ? listUserByRoleDto.getRoleId() : "null");

            // 参数校验
            if (listUserByRoleDto == null || StringUtils.isBlank(listUserByRoleDto.getRoleId())) {
                log.warn("分页获取角色绑定的用户列表失败：角色ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "角色ID不能为空");
            }

            String roleId = listUserByRoleDto.getRoleId();
            String keyWord = listUserByRoleDto.getKeyWord();

            // 分页参数
            int pageNum = listUserByRoleDto.getPageNum() == null ? 1 : listUserByRoleDto.getPageNum();
            int pageSize = listUserByRoleDto.getPageSize() == null ? 10 : listUserByRoleDto.getPageSize();
            if (pageNum < 1) {
                pageNum = 1;
            }
            if (pageSize <= 0) {
                pageSize = 10;
            }

            log.debug("查询条件：roleId: {}, keyWord: {}, pageNum: {}, pageSize: {}", roleId, keyWord, pageNum, pageSize);

            // 获取角色详情，然后获取角色绑定的所有用户id（owner/name，指API可以识别的id）
            org.casbin.casdoor.entity.Role role = roleService.getRole(roleId);
            if (role == null) {
                log.warn("未查询到角色信息，roleId: {}", roleId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "角色不存在");
            }

            String[] users = role.users;
            if (users == null || users.length == 0) {
                log.debug("角色下没有绑定任何用户，roleId: {}", roleId);

                PageDto<com.iflytek.rpa.auth.core.entity.User> emptyPage = new PageDto<>();
                emptyPage.setResult(Collections.emptyList());
                emptyPage.setCurrentPageNo(pageNum);
                emptyPage.setPageSize(pageSize);
                emptyPage.setTotalCount(0L);
                return AppResponse.success(emptyPage);
            }

            log.debug("角色下绑定的用户数量（原始）: {}，roleId: {}", users.length, roleId);

            // 根据用户id获取用户信息，并映射到通用实体，收集到list
            List<com.iflytek.rpa.auth.core.entity.User> userList = new ArrayList<>();
            for (String userId : users) {
                if (userId == null || userId.trim().isEmpty()) {
                    continue;
                }
                try {
                    // userId 形如 owner/name，取 name 部分作为登录名
                    String[] parts = userId.split("/");
                    String userName = parts.length > 1 ? parts[1] : parts[0];

                    User casdoorUser = userExtendService.getUser(userName);
                    if (casdoorUser == null) {
                        log.warn("根据用户名未查询到用户信息，userId: {}, userName: {}", userId, userName);
                        continue;
                    }

                    com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(casdoorUser);
                    if (commonUser != null) {
                        userList.add(commonUser);
                    }
                } catch (Exception e) {
                    log.warn("查询或转换用户信息失败，userId: {}", userId, e);
                }
            }

            log.debug("角色下成功转换为通用用户对象数量: {}，roleId: {}", userList.size(), roleId);

            // 关键字过滤：根据登录名或姓名模糊查询
            if (StringUtils.isNotBlank(keyWord)) {
                String kw = keyWord.trim();
                userList = userList.stream()
                        .filter(u -> u != null
                                && ((u.getLoginName() != null
                                                && u.getLoginName().contains(kw))
                                        || (u.getName() != null && u.getName().contains(kw))))
                        .collect(Collectors.toList());

                log.debug("关键字过滤后用户数量: {}，keyword: {}", userList.size(), kw);
            }

            // 手动分页
            int total = userList.size();
            int fromIndex = (pageNum - 1) * pageSize;
            int toIndex = Math.min(fromIndex + pageSize, total);

            List<com.iflytek.rpa.auth.core.entity.User> pageResult;
            if (fromIndex >= total) {
                pageResult = Collections.emptyList();
            } else {
                pageResult = userList.subList(fromIndex, toIndex);
            }

            PageDto<com.iflytek.rpa.auth.core.entity.User> pageDto = new PageDto<>();
            pageDto.setResult(pageResult);
            pageDto.setCurrentPageNo(pageNum);
            pageDto.setPageSize(pageSize);
            pageDto.setTotalCount((long) total);

            log.debug(
                    "分页获取角色绑定的用户列表成功，roleId: {}，总数: {}，当前页: {}，每页: {}，当前页数量: {}",
                    roleId,
                    total,
                    pageNum,
                    pageSize,
                    pageResult.size());

            return AppResponse.success(pageDto);
        } catch (IOException e) {
            log.error(
                    "分页获取角色绑定的用户列表失败（IO异常），roleId: {}",
                    listUserByRoleDto != null ? listUserByRoleDto.getRoleId() : "null",
                    e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "分页获取角色绑定的用户列表失败: " + e.getMessage());
        } catch (Exception e) {
            log.error(
                    "分页获取角色绑定的用户列表异常，roleId: {}",
                    listUserByRoleDto != null ? listUserByRoleDto.getRoleId() : "null",
                    e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "分页获取角色绑定的用户列表异常: " + e.getMessage());
        }
    }

    /**
     * 获取当前登录用户
     * @param request HTTP请求
     * @return 当前登录用户信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> getCurrentLoginUser(HttpServletRequest request) {
        try {
            // 从session获取当前用户
            User casdoorUser = SessionUserUtils.getUserFromSession(request);

            if (casdoorUser != null) {
                // 使用mapper转换为通用User
                com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(casdoorUser);
                return AppResponse.success(commonUser);
            } else {
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }
        } catch (Exception e) {
            log.error("获取当前登录用户失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前登录用户ID
     * @param request HTTP请求
     * @return 当前登录用户ID
     */
    @Override
    public AppResponse<String> getCurrentUserId(HttpServletRequest request) {
        try {
            // 从session获取当前用户
            User casdoorUser = SessionUserUtils.getUserFromSession(request);

            if (casdoorUser != null) {
                return AppResponse.success(casdoorUser.id);
            } else {
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }
        } catch (Exception e) {
            log.error("获取当前用户ID失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前用户ID失败: " + e.getMessage());
        }
    }

    /**
     * 获取当前登录用户名
     * @param request HTTP请求
     * @return 当前登录用户名
     */
    @Override
    public AppResponse<String> getCurrentLoginUsername(HttpServletRequest request) {
        try {
            // 从session获取当前用户
            User casdoorUser = SessionUserUtils.getUserFromSession(request);

            if (casdoorUser != null) {
                return AppResponse.success(casdoorUser.name);
            } else {
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }
        } catch (Exception e) {
            log.error("获取当前登录用户名失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前登录用户名失败: " + e.getMessage());
        }
    }

    /**
     * 根据用户ID查询登录名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 登录名
     */
    @Override
    public AppResponse<String> getLoginNameById(String id, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(id)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserById(id);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            return AppResponse.success(casdoorUser.name);
        } catch (Exception e) {
            log.error("根据用户ID获取登录名失败: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据用户ID获取登录名失败: " + e.getMessage());
        }
    }

    /**
     * 根据用户ID查询姓名
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户姓名
     */
    @Override
    public AppResponse<String> getRealNameById(String id, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(id)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserById(id);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            return AppResponse.success(casdoorUser.displayName);
        } catch (Exception e) {
            log.error("根据用户ID获取真实姓名失败: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据用户ID获取真实姓名失败: " + e.getMessage());
        }
    }

    /**
     * 根据用户ID查询用户信息
     * @param id 用户ID
     * @param request HTTP请求
     * @return 用户信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> getUserInfoById(String id, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(id)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserById(id);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            // 使用mapper转换为通用User
            com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(casdoorUser);
            return AppResponse.success(commonUser);
        } catch (Exception e) {
            log.error("根据用户ID获取用户信息失败: {}", id, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据用户ID获取用户信息失败: " + e.getMessage());
        }
    }

    /**
     * 根据手机号查询用户姓名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户姓名
     */
    @Override
    public AppResponse<String> getRealNameByPhone(String phone, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(phone)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserByPhone(phone);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            return AppResponse.success(casdoorUser.displayName);
        } catch (Exception e) {
            log.error("根据电话获取用户真实姓名失败: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据电话获取用户真实姓名失败: " + e.getMessage());
        }
    }

    /**
     * 根据手机号查询登录名
     * @param phone 手机号
     * @param request HTTP请求
     * @return 登录名
     */
    @Override
    public AppResponse<String> getLoginNameByPhone(String phone, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(phone)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserByPhone(phone);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            return AppResponse.success(casdoorUser.name);
        } catch (Exception e) {
            log.error("根据电话获取登录名失败: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据电话获取登录名失败: " + e.getMessage());
        }
    }

    /**
     * 判断是否历史用户（ext_info = 1 表示历史用户）
     * @param phone 手机号
     * @return 是否历史用户
     */
    @Override
    public AppResponse<Boolean> isHistoryUser(String phone) {
        try {
            log.debug("判断是否历史用户，phone: {}（Casdoor暂不支持此功能，默认返回false）", phone);
            return AppResponse.success(false);
        } catch (Exception e) {
            log.error("判断是否历史用户异常，phone: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "判断是否历史用户失败: " + e.getMessage());
        }
    }

    /**
     * 根据手机号查询用户信息
     * @param phone 手机号
     * @param request HTTP请求
     * @return 用户信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> getUserInfoByPhone(
            String phone, HttpServletRequest request) {
        try {
            if (Objects.isNull(userExtendService) || Objects.isNull(phone)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "参数错误");
            }

            User casdoorUser = userExtendService.getUserByPhone(phone);
            if (Objects.isNull(casdoorUser)) {
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "用户不存在");
            }

            // 使用mapper转换为通用User
            com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(casdoorUser);
            return AppResponse.success(commonUser);
        } catch (Exception e) {
            log.error("根据电话获取用户信息失败: {}", phone, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据电话获取用户信息失败: " + e.getMessage());
        }
    }

    /**
     * 根据用户ID列表查询用户信息列表（最多支持100个id）
     * @param userIdList 用户ID列表
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.User>> queryUserListByIds(
            List<String> userIdList, HttpServletRequest request) {
        try {
            if (Objects.isNull(userService) || userIdList == null || userIdList.isEmpty()) {
                return AppResponse.success(Collections.emptyList());
            }

            // 限制最多100个ID，去重后组织成Set
            Set<String> limitedUserIds =
                    userIdList.stream().distinct().limit(100).collect(Collectors.toSet());

            List<User> allCasdoorUsers = userService.getUsers();
            List<User> filteredCasdoorUsers = allCasdoorUsers.stream()
                    .filter(user -> limitedUserIds.contains(user.id))
                    .collect(Collectors.toList());

            // 使用mapper转换为通用User列表
            List<com.iflytek.rpa.auth.core.entity.User> commonUsers =
                    filteredCasdoorUsers.stream().map(userMapper::toCommonUser).collect(Collectors.toList());

            return AppResponse.success(commonUsers);
        } catch (IOException e) {
            log.error("根据用户ID列表查询用户信息失败", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "根据用户ID列表查询用户信息失败: " + e.getMessage());
        }
    }

    /**
     * 根据姓名模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.User>> searchUserByName(
            String keyword, String deptId, HttpServletRequest request) {
        try {
            log.debug("开始根据姓名模糊查询人员，keyword: {}", keyword);

            // 参数校验
            if (keyword == null || keyword.trim().isEmpty()) {
                log.warn("根据姓名模糊查询人员失败：关键字为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "关键字不能为空");
            }

            // 获取当前租户ID（owner），可选
            String owner = getCurrentTenantOwner(request);
            // 查询用户列表（限定在当前租户下，如果owner为空则查询全部）
            List<User> casdoorUsers = casdoorUserDao.searchUserByName(keyword, owner, databaseName);
            if (casdoorUsers == null) {
                log.debug("查询结果为空，keyword: {}", keyword);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个用户，keyword: {}", casdoorUsers.size(), keyword);

            // 转换为通用用户对象列表，过滤掉转换失败的对象
            List<com.iflytek.rpa.auth.core.entity.User> userList = casdoorUsers.stream()
                    .filter(user -> user != null)
                    .map(user -> {
                        try {
                            return userMapper.toCommonUser(user);
                        } catch (Exception e) {
                            log.warn("用户信息转换失败，userId: {}, keyword: {}", user != null ? user.id : "null", keyword, e);
                            return null;
                        }
                    })
                    .filter(user -> user != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个用户，keyword: {}", userList.size(), keyword);
            return AppResponse.success(userList);
        } catch (Exception e) {
            log.error("根据姓名模糊查询人员异常，keyword: {}", keyword, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据姓名模糊查询人员失败: " + e.getMessage());
        }
    }

    /**
     * 根据手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.User>> searchUserByPhone(
            String keyword, String deptId, HttpServletRequest request) {
        try {
            log.debug("开始根据手机号模糊查询人员，keyword: {}", keyword);

            // 参数校验
            if (keyword == null || keyword.trim().isEmpty()) {
                log.warn("根据手机号模糊查询人员失败：关键字为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "关键字不能为空");
            }

            // 获取当前租户ID（owner）
            String owner = getCurrentTenantOwner(request);

            // 查询用户列表（限定在当前租户下，如果owner为空则查询全部）
            List<User> casdoorUsers = casdoorUserDao.searchUserByPhone(keyword, owner, databaseName);
            if (casdoorUsers == null) {
                log.debug("查询结果为空，keyword: {}", keyword);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个用户，keyword: {}", casdoorUsers.size(), keyword);

            // 转换为通用用户对象列表，过滤掉转换失败的对象
            List<com.iflytek.rpa.auth.core.entity.User> userList = casdoorUsers.stream()
                    .filter(user -> user != null)
                    .map(user -> {
                        try {
                            return userMapper.toCommonUser(user);
                        } catch (Exception e) {
                            log.warn("用户信息转换失败，userId: {}, keyword: {}", user != null ? user.id : "null", keyword, e);
                            return null;
                        }
                    })
                    .filter(user -> user != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个用户，keyword: {}", userList.size(), keyword);
            return AppResponse.success(userList);
        } catch (Exception e) {
            log.error("根据手机号模糊查询人员异常，keyword: {}", keyword, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据手机号模糊查询人员失败: " + e.getMessage());
        }
    }

    /**
     * 根据姓名或手机号模糊查询人员
     * @param keyword 关键字
     * @param deptId 部门ID（可选）
     * @param request HTTP请求
     * @return 用户信息列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.User>> searchUserByNameOrPhone(
            String keyword, String deptId, HttpServletRequest request) {
        try {
            log.debug("开始根据姓名或手机号模糊查询人员，keyword: {}", keyword);

            // 参数校验
            if (keyword == null || keyword.trim().isEmpty()) {
                log.warn("根据姓名或手机号模糊查询人员失败：关键字为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "关键字不能为空");
            }

            // 获取当前租户ID（owner），可选
            String owner = getCurrentTenantOwner(request);

            // 查询用户列表（限定在当前租户下，如果owner为空则查询全部）
            List<User> casdoorUsers = casdoorUserDao.searchUserByNameOrPhone(keyword, owner, databaseName);
            if (casdoorUsers == null) {
                log.debug("查询结果为空，keyword: {}", keyword);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("查询到 {} 个用户，keyword: {}", casdoorUsers.size(), keyword);

            // 转换为通用用户对象列表，过滤掉转换失败的对象
            List<com.iflytek.rpa.auth.core.entity.User> userList = casdoorUsers.stream()
                    .filter(user -> user != null)
                    .map(user -> {
                        try {
                            return userMapper.toCommonUser(user);
                        } catch (Exception e) {
                            log.warn("用户信息转换失败，userId: {}, keyword: {}", user != null ? user.id : "null", keyword, e);
                            return null;
                        }
                    })
                    .filter(user -> user != null)
                    .collect(Collectors.toList());

            log.debug("成功转换 {} 个用户，keyword: {}", userList.size(), keyword);
            return AppResponse.success(userList);
        } catch (Exception e) {
            log.error("根据姓名或手机号模糊查询人员异常，keyword: {}", keyword, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据姓名或手机号模糊查询人员失败: " + e.getMessage());
        }
    }

    /**
     * 查询当前登录的用户信息
     * @param request HTTP请求
     * @return 用户信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> getUserInfo(HttpServletRequest request) {
        // 与getCurrentLoginUser逻辑相同
        return getCurrentLoginUser(request);
    }

    /**
     * 变更部门
     * @param userChangeDeptDto 变更部门信息
     * @param request HTTP请求
     * @return 变更结果
     */
    @Override
    public AppResponse<String> changeDept(UserChangeDeptDto userChangeDeptDto, HttpServletRequest request) {
        try {
            log.debug("变更部门（Casdoor暂不支持此功能，返回提示信息）");
            return AppResponse.success("Casdoor暂不支持变更部门功能");
        } catch (Exception e) {
            log.error("变更部门异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "变更部门失败: " + e.getMessage());
        }
    }

    /**
     * 删除员工
     * @param userDeleteDto 删除员工信息
     * @param request HTTP请求
     * @return 删除结果
     */
    @Override
    public AppResponse<String> deleteUser(UserDeleteDto userDeleteDto, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始删除员工");

            // 参数校验
            if (userDeleteDto == null || CollectionUtil.isEmpty(userDeleteDto.getUserIdList())) {
                log.warn("删除员工失败：参数为空或用户ID列表为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "用户ID列表不能为空");
            }

            List<String> userIdList = userDeleteDto.getUserIdList();
            log.debug("准备删除 {} 个用户", userIdList.size());

            int successCount = 0;
            int failCount = 0;
            List<String> failUserIds = new ArrayList<>();

            // 循环删除每个用户
            for (String userId : userIdList) {
                try {
                    if (userId == null || userId.trim().isEmpty()) {
                        log.warn("跳过空用户ID");
                        failCount++;
                        continue;
                    }

                    log.debug("开始删除用户，userId: {}", userId);

                    // 先根据id查出来用户name和owner
                    User userById = null;
                    try {
                        userById = userExtendService.getUserById(userId);
                    } catch (Exception e) {
                        log.warn("查询用户失败，userId: {}", userId, e);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    if (userById == null) {
                        log.warn("用户不存在，userId: {}", userId);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    // 调用删除接口
                    log.debug("调用Casdoor API删除用户，userId: {}, name: {}", userId, userById.name);
                    CasdoorResponse<String, Object> deleteUserResponse = userExtendService.deleteUser(userById);

                    // 校验结果
                    if (deleteUserResponse == null) {
                        log.error("删除用户失败：Casdoor API返回为空，userId: {}", userId);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    if (deleteUserResponse.getStatus() != null && !"ok".equals(deleteUserResponse.getStatus())) {
                        log.error(
                                "删除用户失败：Casdoor API返回错误，userId: {}, status: {}, msg: {}",
                                userId,
                                deleteUserResponse.getStatus(),
                                deleteUserResponse.getMsg());
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    log.debug("删除用户成功，userId: {}, name: {}", userId, userById.name);
                    successCount++;
                } catch (Exception e) {
                    log.error("删除用户异常，userId: {}", userId, e);
                    failCount++;
                    failUserIds.add(userId);
                }
            }

            // 返回结果
            if (failCount == 0) {
                log.debug("删除员工成功，共删除 {} 个用户", successCount);
                return AppResponse.success("成功删除 " + successCount + " 个用户");
            } else if (successCount == 0) {
                log.warn("删除员工失败，所有用户删除失败，共 {} 个", failCount);
                return AppResponse.error(
                        ErrorCodeEnum.E_SERVICE,
                        "删除失败，共 " + failCount + " 个用户删除失败，失败用户ID: " + String.join(", ", failUserIds));
            } else {
                log.warn("删除员工部分成功，成功: {}, 失败: {}", successCount, failCount);
                return AppResponse.error(
                        ErrorCodeEnum.E_SERVICE,
                        "部分删除成功，成功: " + successCount + " 个，失败: " + failCount + " 个，失败用户ID: "
                                + String.join(", ", failUserIds));
            }
        } catch (Exception e) {
            log.error("删除员工异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "删除员工异常: " + e.getMessage());
        }
    }

    /**
     * 启用/禁用员工
     * @param userEnableDto 启用/禁用信息
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> enableUser(UserEnableDto userEnableDto, HttpServletRequest request) {
        try {
            log.debug("开始启用/禁用员工");

            // 参数校验
            Integer status = userEnableDto.getStatus();
            if (CollectionUtil.isEmpty(userEnableDto.getUserList()) || status == null) {
                log.warn("启用/禁用员工失败：参数为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "用户列表或状态不能为空");
            }

            if (!status.equals(0) && !status.equals(1)) {
                log.warn("启用/禁用员工失败：状态值无效，status: {}", status);
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "状态值无效，只能为0（停用）或1（启用）");
            }

            String statusText = status == 1 ? "启用" : "停用";
            log.debug("准备{} {} 个用户", statusText, userEnableDto.getUserList().size());

            int successCount = 0;
            int failCount = 0;
            List<String> failUserIds = new ArrayList<>();

            // 循环处理每个用户
            for (UpdateUserDto updateUserDto : userEnableDto.getUserList()) {
                try {
                    if (updateUserDto == null
                            || updateUserDto.getId() == null
                            || updateUserDto.getId().trim().isEmpty()) {
                        log.warn("跳过无效的用户信息");
                        failCount++;
                        continue;
                    }

                    String userId = updateUserDto.getId();
                    log.debug("开始{}用户，userId: {}", statusText, userId);

                    // 先查到对应用户
                    User existingUser = null;
                    try {
                        existingUser = userExtendService.getUserById(userId);
                    } catch (Exception e) {
                        log.warn("查询用户失败，userId: {}", userId, e);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    if (existingUser == null) {
                        log.warn("用户不存在，userId: {}", userId);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    // 更新用户，按照status的值来修改用户的启用状态字段（isForbidden）
                    // status: 0停用 -> isForbidden=true, 1启用 -> isForbidden=false
                    boolean isForbidden = (status == 0);

                    // 如果状态已经相同，跳过
                    if (existingUser.isForbidden == isForbidden) {
                        log.debug("用户状态已经是目标状态，跳过，userId: {}, isForbidden: {}", userId, isForbidden);
                        successCount++;
                        continue;
                    }

                    // 创建更新对象，只更新状态字段
                    User userToUpdate = new User();
                    userToUpdate.id = existingUser.id;
                    userToUpdate.name = existingUser.name;
                    userToUpdate.owner = existingUser.owner;
                    userToUpdate.displayName = existingUser.displayName;
                    userToUpdate.phone = existingUser.phone;
                    userToUpdate.email = existingUser.email;
                    userToUpdate.isForbidden = isForbidden;
                    userToUpdate.isAdmin = existingUser.isAdmin;
                    userToUpdate.isGlobalAdmin = existingUser.isGlobalAdmin;
                    userToUpdate.type = existingUser.type != null ? existingUser.type : "normal-user";
                    userToUpdate.password = existingUser.password != null ? existingUser.password : "";
                    userToUpdate.passwordSalt = existingUser.passwordSalt != null ? existingUser.passwordSalt : "";
                    userToUpdate.isDeleted = existingUser.isDeleted;
                    userToUpdate.emailVerified = existingUser.emailVerified;
                    userToUpdate.createdTime = existingUser.createdTime;
                    userToUpdate.updatedTime = formatDateTime(new Date());
                    userToUpdate.properties = existingUser.properties;
                    userToUpdate.roles = existingUser.roles;
                    userToUpdate.permissions = existingUser.permissions;
                    userToUpdate.address = existingUser.address;
                    userToUpdate.location = existingUser.location;
                    userToUpdate.bio = existingUser.bio;
                    userToUpdate.idCard = existingUser.idCard;
                    userToUpdate.birthday = existingUser.birthday;

                    // 调用更新接口
                    log.debug("调用Casdoor API{}用户，userId: {}, isForbidden: {}", statusText, userId, isForbidden);
                    CasdoorResponse<String, Object> updateUserResponse = userExtendService.updateUser(userToUpdate);

                    // 校验结果
                    if (updateUserResponse == null) {
                        log.error("{}用户失败：Casdoor API返回为空，userId: {}", statusText, userId);
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    if (updateUserResponse.getStatus() != null && !"ok".equals(updateUserResponse.getStatus())) {
                        log.error(
                                "{}用户失败：Casdoor API返回错误，userId: {}, status: {}, msg: {}",
                                statusText,
                                userId,
                                updateUserResponse.getStatus(),
                                updateUserResponse.getMsg());
                        failCount++;
                        failUserIds.add(userId);
                        continue;
                    }

                    log.debug("{}用户成功，userId: {}", statusText, userId);
                    successCount++;
                } catch (Exception e) {
                    log.error(
                            "{}用户异常，userId: {}", statusText, updateUserDto != null ? updateUserDto.getId() : "null", e);
                    failCount++;
                    failUserIds.add(updateUserDto != null ? updateUserDto.getId() : "unknown");
                }
            }

            // 返回结果
            if (failCount == 0) {
                log.debug("{}员工成功，共{} {} 个用户", statusText, statusText, successCount);
                return AppResponse.success("成功" + statusText + " " + successCount + " 个用户");
            } else if (successCount == 0) {
                log.warn("{}员工失败，所有用户{}失败，共 {} 个", statusText, statusText, failCount);
                return AppResponse.error(
                        ErrorCodeEnum.E_SERVICE,
                        statusText + "失败，共 " + failCount + " 个用户" + statusText + "失败，失败用户ID: "
                                + String.join(", ", failUserIds));
            } else {
                log.warn("{}员工部分成功，成功: {}, 失败: {}", statusText, successCount, failCount);
                return AppResponse.error(
                        ErrorCodeEnum.E_SERVICE,
                        "部分" + statusText + "成功，成功: " + successCount + " 个，失败: " + failCount + " 个，失败用户ID: "
                                + String.join(", ", failUserIds));
            }
        } catch (Exception e) {
            log.error("启用/禁用员工异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "启用/禁用员工异常: " + e.getMessage());
        }
    }

    /**
     * 查询当前机构的全部用户(部门新增，部门负责人下拉框)
     * @param orgId 机构ID（对应Casdoor的Group name）
     * @param request HTTP请求
     * @return 用户列表
     */
    @Override
    public AppResponse<List<com.iflytek.rpa.auth.core.entity.User>> queryUserDetailListByOrgId(
            String orgId, HttpServletRequest request) throws IOException {
        try {
            log.debug("开始查询当前机构的全部用户，orgId: {}", orgId);

            // 参数校验
            if (orgId == null || orgId.trim().isEmpty()) {
                log.warn("查询当前机构全部用户失败：机构ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "机构ID不能为空");
            }

            // 调用Casdoor扩展服务查询指定组织下的用户id（owner/name）列表
            Group group = null;
            try {
                group = casdoorGroupExtendService.getGroup(orgId);
            } catch (Exception e) {
                log.error("根据机构ID查询Casdoor群组信息失败，orgId: {}", orgId, e);
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "查询机构信息失败: " + e.getMessage());
            }

            if (group == null) {
                log.warn("根据机构ID未查询到Casdoor群组信息，orgId: {}", orgId);
                return AppResponse.error(ErrorCodeEnum.E_NO_ACCOUNT, "机构不存在");
            }

            List<String> userIds = group.users;
            if (userIds == null || userIds.isEmpty()) {
                log.debug("当前机构下未查询到用户，orgId: {}", orgId);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("当前机构下查询到 {} 个绑定用户ID（owner/name），orgId: {}", userIds.size(), orgId);

            // 根据用户id(owner/name)查询用户信息，过程中任何单个用户失败不影响其他用户
            List<User> users = userIds.stream()
                    .filter(Objects::nonNull)
                    .map(userId -> {
                        try {
                            String[] parts = userId.split("/");
                            if (parts.length < 2 || parts[1].trim().isEmpty()) {
                                log.warn("用户ID格式不正确，期望为owner/name，实际为: {}", userId);
                                return null;
                            }
                            String name = parts[1].trim();
                            return userExtendService.getUser(name);
                        } catch (IOException ioEx) {
                            log.warn("根据用户ID查询Casdoor用户失败（IO异常），userId: {}", userId, ioEx);
                            return null;
                        } catch (Exception ex) {
                            log.warn("根据用户ID查询Casdoor用户失败，userId: {}", userId, ex);
                            return null;
                        }
                    })
                    .filter(Objects::nonNull)
                    .collect(Collectors.toList());

            if (users.isEmpty()) {
                log.debug("当前机构下所有绑定用户ID均未能成功查询到用户信息，orgId: {}", orgId);
                return AppResponse.success(Collections.emptyList());
            }

            // 转换为通用User列表
            List<com.iflytek.rpa.auth.core.entity.User> commonUsers = users.stream()
                    .filter(Objects::nonNull)
                    .map(u -> {
                        try {
                            return userMapper.toCommonUser(u);
                        } catch (Exception e) {
                            log.warn("用户信息转换失败，userId: {}", u != null ? u.id : "null", e);
                            return null;
                        }
                    })
                    .filter(Objects::nonNull)
                    .collect(Collectors.toList());

            log.debug("当前机构下成功转换 {} 个通用用户对象，orgId: {}", commonUsers.size(), orgId);
            return AppResponse.success(commonUsers);
        } catch (Exception e) {
            log.error("查询当前机构全部用户异常，orgId: {}", orgId, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "查询当前机构全部用户异常: " + e.getMessage());
        }
    }

    /**
     * 卓越中心-机器人看板-所有者下拉选择-查询接口
     * 跟据输入的关键字（姓名或手机号）查询用户
     * @param keyword 关键字（姓名或手机号）
     * @param deptId 部门ID(仅兼容接口用)
     * @return 用户搜索结果列表
     */
    @Override
    public AppResponse<List<UserSearchDto>> getUserByNameOrPhone(
            String keyword, String deptId, HttpServletRequest request) {
        try {
            log.debug("开始根据姓名或手机号查询用户，keyword: {}", keyword);

            // 参数校验
            if (keyword == null || keyword.trim().isEmpty()) {
                log.warn("根据姓名或手机号查询用户失败：关键字为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "关键字不能为空");
            }

            // 获取当前租户ID（owner），限定查询范围
            String owner = getCurrentTenantOwner(request);

            // 调用DAO按姓名或手机号模糊查询（在当前租户范围内）
            List<User> casdoorUsers = casdoorUserDao.searchUserByNameOrPhone(keyword.trim(), owner, databaseName);
            if (casdoorUsers == null || casdoorUsers.isEmpty()) {
                log.debug("根据姓名或手机号查询用户结果为空，keyword: {}", keyword);
                return AppResponse.success(Collections.emptyList());
            }

            log.debug("根据姓名或手机号查询到 {} 个用户，keyword: {}", casdoorUsers.size(), keyword);

            // 转为简洁的 UserSearchDto 列表
            List<UserSearchDto> result = casdoorUsers.stream()
                    .filter(Objects::nonNull)
                    .map(u -> {
                        UserSearchDto dto = new UserSearchDto();
                        dto.setId(u.id);
                        dto.setName(u.name);
                        dto.setPhone(u.phone);
                        return dto;
                    })
                    .collect(Collectors.toList());

            log.debug("根据姓名或手机号查询用户成功，返回 {} 条结果，keyword: {}", result.size(), keyword);
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("根据姓名或手机号查询用户异常，keyword: {}", keyword, e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据姓名或手机号查询用户异常: " + e.getMessage());
        }
    }

    /**
     * 获取用户详细信息
     * @param tenantId 租户ID
     * @param getUserDto 查询参数
     * @param request HTTP请求
     * @return 用户扩展信息
     */
    @Override
    public AppResponse<UserExtendDto> queryUserExtendInfo(
            String tenantId, GetUserDto getUserDto, HttpServletRequest request) throws IOException {
        UserExtendDto userExtendDto = new UserExtendDto();
        User userById = null;
        User userByName = null;

        // 按id查
        if (Objects.nonNull(getUserDto.getUserId())) {
            userById = userExtendService.getUserById(getUserDto.getUserId());
        }

        // 按name查
        if (Objects.nonNull(getUserDto.getLoginName())) {
            userByName = userExtendService.getUser(getUserDto.getLoginName());
        }

        // 查不到结果返回空
        if (userById == null && userByName == null) {
            return AppResponse.success(userExtendDto);
        }
        // 如果id和name查出的结果不是对应的，返回空
        if (userById != null && userByName != null && !StringUtils.equals(userById.id, userByName.id)) {
            return AppResponse.success(userExtendDto);
        }

        // 转为通用user
        com.iflytek.rpa.auth.core.entity.User commonUser =
                userMapper.toCommonUser(userById == null ? userByName : userById);

        userExtendDto.setUser(commonUser);

        return AppResponse.success(userExtendDto);
    }

    /**
     * 获取当前用户权限列表
     * @param request HTTP请求
     * @return 用户权限列表
     */
    @Override
    public AppResponse<List<Permission>> getCurrentUserPermissionList(HttpServletRequest request) throws IOException {
        try {
            // 从session获取当前用户
            User casdoorUser = SessionUserUtils.getUserFromSession(request);

            if (casdoorUser != null && casdoorUser.permissions != null) {
                // 使用mapper将Casdoor Permission转换为通用Permission
                List<Permission> commonPermissions = casdoorUser.permissions.stream()
                        .map(permissionMapper::toCommonPermission)
                        .collect(Collectors.toList());

                return AppResponse.success(commonPermissions);
            } else if (casdoorUser != null) {
                // 如果用户没有权限列表，返回空列表
                return AppResponse.success(Collections.emptyList());
            } else {
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户未登录");
            }
        } catch (Exception e) {
            log.error("获取当前用户权限列表失败", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取当前用户权限列表失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<UserEntitlementDto> getCurrentUserEntitlement(HttpServletRequest request) {
        UserEntitlementDto userEntitlementDto = new UserEntitlementDto();
        userEntitlementDto.setModuleConsole(true);
        userEntitlementDto.setModuleDesigner(true);
        userEntitlementDto.setModuleExecutor(true);
        userEntitlementDto.setModuleMarket(true);
        return AppResponse.success(userEntitlementDto);
    }

    @Override
    public AppResponse<String> getNameById(String id, HttpServletRequest request) {
        return AppResponse.success("");
    }

    @Override
    public AppResponse<PageDto<RobotExecute>> getDeployedUserList(
            GetDeployedUserListDto dto, HttpServletRequest request) {
        return AppResponse.success(new PageDto<>());
    }

    @Override
    public AppResponse<List<MarketDto>> getUserUnDeployed(GetUserUnDeployedDto dto, HttpServletRequest request) {
        return AppResponse.success(new ArrayList<>());
    }

    @Override
    public AppResponse<PageDto<MarketDto>> getMarketUserList(GetMarketUserListDto dto, HttpServletRequest request) {
        try {
            if (dto.getPageNo() == null || dto.getPageNo() < 1) {
                dto.setPageNo(1);
            }
            if (dto.getPageSize() == null || dto.getPageSize() < 1) {
                dto.setPageSize(10);
            }
            Page<MarketDto> page = new Page<>(dto.getPageNo(), dto.getPageSize(), true);
            // 获取市场下的用户列表
            IPage<MarketDto> result = casdoorUserDao.getMarketUserList(page, dto, databaseName);

            PageDto<MarketDto> pageDto = new PageDto<>();
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
    public AppResponse<PageDto<MarketDto>> getMarketUserListByPublic(
            GetMarketUserListByPublicDto dto, HttpServletRequest request) {
        return AppResponse.success(new PageDto<>());
    }

    @Override
    public AppResponse<List<MarketDto>> getMarketUserByPhone(GetMarketUserByPhoneDto dto, HttpServletRequest request) {
        try {
            log.debug("开始根据手机号或姓名查询市场用户，marketId: {}, keyword: {}", 
                    dto != null ? dto.getMarketId() : "null", 
                    dto != null ? dto.getKeyword() : "null");

            // 参数校验
            if (dto == null || StringUtils.isBlank(dto.getMarketId())) {
                log.warn("根据手机号或姓名查询市场用户失败：参数为空或marketId为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "市场ID不能为空");
            }

            // 调用DAO查询
            List<MarketDto> result = casdoorUserDao.getMarketUserByPhone(dto, databaseName);
            if (result == null) {
                result = Collections.emptyList();
            }

            log.debug("根据手机号或姓名查询市场用户成功，返回 {} 条结果，marketId: {}", result.size(), dto.getMarketId());
            return AppResponse.success(result);
        } catch (Exception e) {
            log.error("根据手机号或姓名查询市场用户异常，marketId: {}", 
                    dto != null ? dto.getMarketId() : "null", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "根据手机号或姓名查询市场用户失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<List<MarketDto>> getMarketUserByPhoneForOwner(
            GetMarketUserByPhoneForOwnerDto dto, HttpServletRequest request) {
        return AppResponse.success(new ArrayList<>());
    }

    @Override
    public AppResponse<List<TenantUser>> getMarketTenantUserList(
            GetMarketTenantUserListDto dto, HttpServletRequest request) {
        return null;
    }

    @Override
    public AppResponse<String> logout(HttpServletRequest request, HttpServletResponse response) throws IOException {
        try {
            log.debug("开始登出");

            // 从请求中获取casdoor的session id
            String casdoorSessionId = casdoorLoginExtendService.extractCasdoorSessionIdFromRequest(request);
            if (casdoorSessionId == null || casdoorSessionId.isEmpty()) {
                log.warn("登出失败：Casdoor session ID为空");
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "Session ID不能为空");
            }

            //            // 获取当前用户的access token
            //            String accessToken = null;
            //            try {
            //                Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            //                if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails)
            // {
            //                    CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            //                    User currentUser = userDetails.getUser();
            //                    if (currentUser != null && currentUser.name != null && !currentUser.name.isEmpty()) {
            //                        accessToken = TokenManager.getAccessToken(currentUser.name);
            //                        log.debug("获取到当前用户的access token，username: {}", currentUser.name);
            //
            //                        // 登出时清除Redis中的token
            //                        TokenManager.clearTokens(currentUser.name);
            //                    }
            //                }
            //            } catch (Exception e) {
            //                log.warn("获取当前用户access token失败", e);
            //            }
            //
            //            if (accessToken == null || accessToken.isEmpty()) {
            //                log.warn("获取当前用户access token为空，可能token已过期或不存在");
            //                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取用户access token失败，请重新登录");
            //            }

            // 用session调用logout
            log.debug("调用Casdoor登出接口，sessionId: {}", casdoorSessionId);
            casdoorLoginExtendService.logout(casdoorSessionId);

            log.debug("登出成功");
            return AppResponse.success("登出成功！");
        } catch (IOException e) {
            log.error("登出失败（IO异常）", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "登出失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("登出异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "登出异常: " + e.getMessage());
        }
    }

    /**
     * 获取Casdoor登录重定向URL（Casdoor专用，备用）
     * @param request HTTP请求
     * @return 登录重定向URL
     */
    @Override
    public AppResponse<String> getRedirectUrl(HttpServletRequest request) {
        try {
            log.debug("开始获取Casdoor登录重定向URL");

            if (StringUtils.isBlank(redirectUrl)) {
                log.warn("获取登录重定向URL失败：redirectUrl配置为空");
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "redirectUrl配置为空");
            }

            // 调用Casdoor扩展服务获取登录URL
            String signinUrl = casdoorAuthExtendService.getCustomSigninUrl(redirectUrl);

            // 使用外部endpoint返回给前端，确保前端能访问到正确的地址
            String fullUrl =
                    externalEndPoint != null && !externalEndPoint.isEmpty() ? externalEndPoint + signinUrl : signinUrl;

            log.debug("获取Casdoor登录重定向URL成功: {}", fullUrl);
            return AppResponse.success(fullUrl);
        } catch (org.casbin.casdoor.exception.AuthException e) {
            log.error("Casdoor认证异常", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "获取登录重定向URL失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("获取登录重定向URL异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取登录重定向URL异常: " + e.getMessage());
        }
    }

    /**
     * Casdoor OAuth登录（Casdoor专用，备用）
     * @param code OAuth授权码
     * @param state OAuth state参数
     * @param request HTTP请求
     * @return 用户信息
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> signIn(
            String code, String state, HttpServletRequest request) throws IOException {
        //        try {
        //            log.debug("开始Casdoor OAuth登录，code: {}, state: {}", code, state);
        //
        //            // 参数校验
        //            if (StringUtils.isBlank(code)) {
        //                log.warn("OAuth登录失败：授权码为空");
        //                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "授权码不能为空");
        //            }
        //
        //            OAuthJSONAccessTokenResponse oAuthTokenResponse =
        // casdoorAuthExtendService.getOAuthTokenResponse(code, state);
        //            String accessToken = oAuthTokenResponse.getAccessToken();
        //            String refreshToken = oAuthTokenResponse.getRefreshToken();
        //            String idToken = accessToken;
        //            // 动态获取系统内置证书，在initDataNewOnly为true时，证书会被篡改
        //            ApplicationExtend applicationWithKey =
        // applicationExtendService.getApplicationWithKey("app-built-in");
        //            // 使用idToken解析用户信息（这是OIDC的核心：从id_token获取用户身份）
        //            User user = authExtendService.parseJwtTokenWithCertificate(idToken,
        // applicationWithKey.certPublicKey);
        //
        //            // 1. 将用户信息存储到session中（Spring Session自动管理Redis存储）
        //            HttpSession session = request.getSession();
        //            session.setAttribute("user", user);
        //
        //            // 2. 设置Spring Security认证上下文
        //            CustomUserDetails userDetails = new CustomUserDetails(user);
        //            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
        //                    userDetails, null, AuthorityUtils.createAuthorityList("ROLE_USER"));
        //            authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
        //            SecurityContextHolder.getContext().setAuthentication(authentication);
        //
        //            // 3. accessToken和refreshToken存储到Redis，供服务端调用Casdoor API使用
        //            long tokenExpireTime = 24 * 60 * 60; // 24小时过期时间（秒）
        //            TokenManager.storeTokens(user.name, accessToken, refreshToken, tokenExpireTime);
        //
        //            log.info("用户 {} 登录成功，session和认证上下文已设置，服务端token已存储", user.name);
        //
        //            // 6. 转换为通用User对象
        //            com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(user);
        //
        //            log.info("用户 {} OAuth登录成功，session和认证上下文已设置，服务端token已存储", user.name);
        //            return AppResponse.success(commonUser);
        //        } catch (org.casbin.casdoor.exception.AuthException e) {
        //            log.error("Casdoor认证异常", e);
        //            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "OAuth登录失败: " + e.getMessage());
        //        } catch (Exception e) {
        //            log.error("OAuth登录异常", e);
        //            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "OAuth登录异常: " + e.getMessage());
        //        }
        return null;
    }

    /**
     * 检查用户登录状态（Casdoor专用）
     * @param request HTTP请求
     * @return 用户信息，如果未登录返回错误
     */
    @Override
    public AppResponse<com.iflytek.rpa.auth.core.entity.User> checkLoginStatus(HttpServletRequest request) {
        try {
            log.debug("开始检查用户登录状态");

            // 1. 检查session是否存在
            javax.servlet.http.HttpSession session = request.getSession(false);
            if (session == null) {
                log.warn("检查登录状态失败：session不存在");
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "未登录");
            }

            // 2. 从session中获取用户信息
            User casdoorUser = (User) session.getAttribute("user");
            if (casdoorUser == null) {
                log.warn("检查登录状态失败：用户信息不存在");
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户信息不存在");
            }

            // 3. 检查服务端token是否还有效
            boolean hasToken = TokenManager.hasToken(casdoorUser.name);
            if (!hasToken) {
                log.warn("检查登录状态失败：服务端token已过期，username: {}", casdoorUser.name);
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "服务端token已过期，请重新登录");
            }

            // 4. 转换为通用User对象
            com.iflytek.rpa.auth.core.entity.User commonUser = userMapper.toCommonUser(casdoorUser);

            log.debug("检查登录状态成功，用户已登录，username: {}", casdoorUser.name);
            return AppResponse.success(commonUser);
        } catch (Exception e) {
            log.error("检查登录状态异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "检查登录状态失败: " + e.getMessage());
        }
    }

    /**
     * 刷新服务端token（Casdoor专用，当accessToken过期时使用）
     * @param request HTTP请求
     * @return 操作结果
     */
    @Override
    public AppResponse<String> refreshToken(HttpServletRequest request) {
        try {
            log.debug("开始刷新服务端token");

            // 1. 从session中获取用户信息
            javax.servlet.http.HttpSession session = request.getSession(false);
            if (session == null) {
                log.warn("刷新token失败：session不存在");
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "未登录");
            }

            User casdoorUser = (User) session.getAttribute("user");
            if (casdoorUser == null) {
                log.warn("刷新token失败：用户信息不存在");
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "未登录");
            }

            // 2. 从Redis获取refreshToken
            String refreshToken = TokenManager.getRefreshToken(casdoorUser.name);
            if (refreshToken == null || refreshToken.isEmpty()) {
                log.warn("刷新token失败：RefreshToken不存在，username: {}", casdoorUser.name);
                return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "RefreshToken不存在，请重新登录");
            }

            // 3. 使用refreshToken获取新的token
            org.apache.oltu.oauth2.client.response.OAuthJSONAccessTokenResponse newTokenResponse =
                    casdoorAuthExtendService.refreshToken(refreshToken, "read");

            if (newTokenResponse == null) {
                log.error("刷新token失败：获取新token响应为空");
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "刷新token失败：响应为空");
            }

            String newAccessToken = newTokenResponse.getAccessToken();
            String newRefreshToken = newTokenResponse.getRefreshToken();

            if (StringUtils.isBlank(newAccessToken)) {
                log.error("刷新token失败：新accessToken为空");
                return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "刷新token失败：新accessToken为空");
            }

            // 4. 更新Redis中的token
            long tokenExpireTime = 24 * 60 * 60; // 24小时过期时间（秒）
            TokenManager.storeTokens(
                    casdoorUser.name,
                    newAccessToken,
                    newRefreshToken != null ? newRefreshToken : refreshToken,
                    tokenExpireTime);

            log.info("用户 {} 的服务端token已刷新", casdoorUser.name);
            return AppResponse.success("Token刷新成功");
        } catch (org.casbin.casdoor.exception.AuthException e) {
            log.error("Casdoor认证异常", e);
            return AppResponse.error(ErrorCodeEnum.E_API_EXCEPTION, "刷新token失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("刷新token异常", e);
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "刷新token失败: " + e.getMessage());
        }
    }

    @Override
    public AppResponse<PageDto<RobotExecute>> getDeployedUserListWithoutTenantId(
            GetDeployedUserListDto dto, HttpServletRequest request) {
        return AppResponse.success(new PageDto<RobotExecute>());
    }
}
